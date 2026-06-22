from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Venda
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.cliente_schema import ClienteCreate


class VendaRepository(BaseRepository[Venda]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Venda]:
        return Venda
