from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import PontoDeVenda
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.pvd_schema import PontoDeVendaCreate


class PvdRepository(BaseRepository[PontoDeVenda]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[PontoDeVenda]:
        return PontoDeVenda
