from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.database import get_session
from apisisbro.repository.insumo_repository import InsumoRepository
from apisisbro.services.insumo_service import InsumoService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_insumo_repository(db: SessionDep) -> InsumoRepository:
    return InsumoRepository(db)


def get_insumo_service(
    repo: Annotated[InsumoRepository, Depends(get_insumo_repository)],
) -> InsumoService:
    return InsumoService(repo)


InsumoServiceDep = Annotated[InsumoService, Depends(get_insumo_service)]
