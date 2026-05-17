from collections.abc import Sequence

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

    async def get_product_by_name(self, nome: str) -> Produto | None:
        return await self.get_by_name(nome, field=nome)

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
