from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Insumo
from apisisbro.repository.base_repository import BaseRepository


class InsumoRepository(BaseRepository[Insumo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Insumo]:
        return Insumo

    async def get_insumo_by_name(self, nome: str) -> Insumo | None:
        return await self.get_by_name(nome, field="nome")
