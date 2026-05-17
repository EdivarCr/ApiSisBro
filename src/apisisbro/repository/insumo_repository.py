from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Insumo
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.producao_schema import FilterInsumo


class InsumoRepository(BaseRepository[Insumo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Insumo]:
        return Insumo

    async def get_insumo_by_name(self, nome: str) -> Insumo | None:
        return await self.get_by_name(nome, field='nome')

    async def get_product_by_filter(self, filter: FilterInsumo) -> Sequence[Insumo]:
        filters = filter.model_dump(exclude={'offset', 'limit'}, exclude_none=True)
        return await self.get_all_by_filter(
            filters,
            like_fields={'nome'},
            limit=filter.limit,
            offset=filter.offset,
        )
