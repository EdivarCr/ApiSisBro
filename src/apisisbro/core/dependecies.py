from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.database import get_session
from apisisbro.repository import (
    EntradaInsumoRepository,
    InsumoRepository,
    ProductionRepository,
    ProductRepository,
)
from apisisbro.services import EntradaInsumoService, InsumoService, ProductionService

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


def get_production_repository(db: SessionDep) -> ProductionRepository:
    return ProductionRepository(db)


def get_product_repository(db: SessionDep) -> ProductRepository:
    return ProductRepository(db)


def get_production_service(
    repo: Annotated[ProductionRepository, Depends(get_production_repository)],
    repoProduct: Annotated[ProductRepository, Depends(get_product_repository)],
) -> ProductionService:
    return ProductionService(repo, repoProduct)


ProductionServiceDep = Annotated[ProductionService, Depends(get_production_service)]
