from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Insumo, Produto, ProdutoInsumo
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.schema import FilterProduct, ProdutoCreate


class ProductRepository(BaseRepository[Produto]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Produto]:
        return Produto

    async def get_product_by_name(self, nome: str) -> Produto | None:
        return await self.get_by_name(nome, field='nome')

    async def get_product_by_filter(self, filter: FilterProduct) -> Sequence[Produto]:
        filters = filter.model_dump(exclude={'offset', 'limit'}, exclude_none=True)
        return await self.get_all_by_filter(
            filters,
            like_fields={'nome'},
            limit=filter.limit,
            offset=filter.offset,
        )

    async def update_image(self, bucket: str, path: str, product: Produto) -> Produto:
        product.imagem_bucket = bucket
        product.imagem_path = path

        await self.session.flush()
        await self.session.refresh(product)

        return product

    async def create_product_with_recipe(
        self, product: ProdutoCreate, user_id: int
    ) -> Produto:
        insumo_ids = [item.insumo_id for item in product.receita]
        unique_ids = set(insumo_ids)

        if len(unique_ids) != len(insumo_ids):
            raise ValueError('A receita não pode conter insumos repetidos.')

        existing_ids = set(
            await self.session.scalars(
                select(Insumo.id).where(Insumo.id.in_(unique_ids))
            )
        )
        missing_ids = sorted(unique_ids - existing_ids)
        if missing_ids:
            raise ValueError(f'Insumos não encontrados: {missing_ids}')

        product_data = product.model_dump(exclude={'receita'})
        db_product = Produto(**product_data, criador_id=user_id)
        self.session.add(db_product)
        await self.session.flush()

        for item in product.receita:
            self.session.add(
                ProdutoInsumo(
                    produto_id=db_product.id,
                    insumo_id=item.insumo_id,
                    quantidade_necessaria=item.quantidade_necessaria,
                )
            )

        await self.session.flush()
        await self.session.refresh(db_product)
        return db_product
