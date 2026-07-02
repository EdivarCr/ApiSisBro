from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apisisbro.models.models import Venda
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.cliente_schema import ClienteCreate


class VendaRepository(BaseRepository[Venda]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Venda]:
        return Venda

    async def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[Venda]:
        query = (
            select(Venda).options(selectinload(Venda.itens)).limit(limit).offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Venda | None:
        query = select(Venda).where(Venda.id == id).options(selectinload(Venda.itens))
        result = await self.session.execute(query)
        return result.scalars().first()
