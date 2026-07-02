from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        query = select(Produto).options(selectinload(Produto.formulas))
        like_fields = {'nome'}

        for field, value in filters.items():
            if not hasattr(Produto, field):
                raise AttributeError(f"{Produto.__name__} não possui o campo '{field}'")

            column = getattr(Produto, field)
            if field in like_fields and isinstance(value, str):
                query = query.where(column.ilike(f'%{value}%'))
            else:
                query = query.where(column == value)

        result = await self.session.scalars(
            query.offset(filter.offset).limit(filter.limit)
        )
        return result.all()

    async def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[Produto]:
        result = await self.session.scalars(
            select(Produto)
            .options(selectinload(Produto.formulas))
            .limit(limit)
            .offset(offset)
        )
        return result.all()

    async def update_image(self, bucket: str, path: str, product: Produto) -> Produto:
        product.imagem_bucket = bucket
        product.imagem_path = path

        await self.session.flush()
        await self.session.refresh(product)

        return product

    async def create_product_with_recipe(
        self, product: ProdutoCreate, user_id: int
    ) -> Produto:
        insumo_ids = [item.insumo_id for item in product.formulas]
        unique_ids = set(insumo_ids)

        if len(unique_ids) != len(insumo_ids):
            raise ValueError('A formula não pode conter insumos repetidos.')

        existing_ids = set(
            await self.session.scalars(select(Insumo.id).where(Insumo.id.in_(unique_ids)))
        )
        missing_ids = sorted(unique_ids - existing_ids)
        if missing_ids:
            raise ValueError(f'Insumos não encontrados: {missing_ids}')

        product_data = product.model_dump(exclude={'formulas'})
        db_product = Produto(**product_data, criador_id=user_id)
        self.session.add(db_product)
        await self.session.flush()

        for item in product.formulas:
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

    async def get_by_id_with_formulas(self, id: int) -> Produto | None:
        return await self.session.scalar(
            select(Produto)
            .options(selectinload(Produto.formulas))
            .where(Produto.id == id)
        )
