from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apisisbro.models.models import Cliente
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.cliente_schema import ClienteCreate


class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Cliente]:
        return Cliente

    async def get_by_id(self, id: int) -> Cliente | None:
        query = (
            select(Cliente).where(Cliente.id == id).options(selectinload(Cliente.vendas))
        )
        result = await self.session.execute(query)
        return result.scalars().first()
