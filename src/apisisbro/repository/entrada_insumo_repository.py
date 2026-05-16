from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import EntradaInsumo
from apisisbro.repository.base_repository import BaseRepository


class EntradaInsumoRepository(BaseRepository[EntradaInsumo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[EntradaInsumo]:
        return EntradaInsumo

    async def get_insumo_by_name(self, nome: str) -> EntradaInsumo | None:
        return await self.get_by_name(nome, field='nome')
