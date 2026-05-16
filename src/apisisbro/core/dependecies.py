from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.database import get_session
from apisisbro.repository.entrada_insumo_repository import EntradaInsumoRepository
from apisisbro.repository.insumo_repository import InsumoRepository
from apisisbro.services.entrada_insumo_service import EntradaInsumoService
from apisisbro.services.insumo_service import InsumoService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_insumo_repository(db: SessionDep) -> InsumoRepository:
    return InsumoRepository(db)


def get_insumo_service(
    repo: Annotated[InsumoRepository, Depends(get_insumo_repository)],
) -> InsumoService:
    return InsumoService(repo)


InsumoServiceDep = Annotated[InsumoService, Depends(get_insumo_service)]


def get_entrada_insumo_repository(db: SessionDep) -> EntradaInsumoRepository:
    return EntradaInsumoRepository(db)


def get_entrada_insumo_service(
    repo: Annotated[EntradaInsumoRepository, Depends(get_entrada_insumo_repository)],
    repoInsumo: Annotated[InsumoRepository, Depends(get_insumo_repository)],
) -> EntradaInsumoService:
    return EntradaInsumoService(repo, repoInsumo)


EntradaInsumoServideDep = Annotated[
    EntradaInsumoService, Depends(get_entrada_insumo_service)
]
