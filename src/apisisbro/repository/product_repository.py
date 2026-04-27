from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Produto
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.schema import FilterProduct


class ProductRepository(BaseRepository[Produto]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Produto]:
        return Produto

    async def get_product_by_name(self, name_product: str) -> Produto | None:
        return await self.session.scalar(
            select(Produto).where(Produto.nome == name_product)
        )

    async def get_product_by_filter(self, filter: FilterProduct) -> Sequence[Produto]:
        query = select(Produto)

        if filter.nome is not None:
            query = query.where(Produto.nome.ilike(f'%{filter.nome}%'))

        if filter.ativo is not None:
            query = query.filter(Produto.ativo == filter.ativo)

        if filter.tem_carolina_reaper is not None:
            query = query.filter(
                Produto.tem_carolina_reaper == filter.tem_carolina_reaper
            )

        if filter.tipo is not None:
            query = query.filter(Produto.tipo == filter.tipo)

        if filter.nivel_picancia is not None:
            query = query.filter(Produto.nivel_picancia == filter.nivel_picancia)

        result = await self.session.scalars(
            query.offset(filter.offset).limit(filter.limit)
        )

        return result.all()

    async def update_image(self, bucket: str, path: str, product: Produto) -> Produto:
        product.imagem_bucket = bucket
        product.imagem_path = path

        await self.session.flush()
        await self.session.refresh(product)

        return product
