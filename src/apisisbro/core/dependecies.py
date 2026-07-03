from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.database import get_session
from apisisbro.repository import (
    ClienteRepository,
    EntradaInsumoRepository,
    InsumoRepository,
    ProductionRepository,
    ProductRepository,
    PvdRepository,
    VendaRepository,
)
from apisisbro.services import (
    ClientService,
    EntradaInsumoService,
    InsumoService,
    ProductionService,
    PvdService,
    VendaService,
)

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
    db: SessionDep,
) -> ProductionService:
    return ProductionService(repo, repoProduct, db)


ProductionServiceDep = Annotated[ProductionService, Depends(get_production_service)]


def get_client_repository(db: SessionDep) -> ClienteRepository:
    return ClienteRepository(db)


def get_client_service(
    repo: Annotated[ClienteRepository, Depends(get_client_repository)],
) -> ClientService:
    return ClientService(repo)


ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]


def get_pvd_repository(db: SessionDep) -> PvdRepository:
    return PvdRepository(db)


def get_pvd_service(
    repo: Annotated[PvdRepository, Depends(get_pvd_repository)],
) -> PvdService:
    return PvdService(repo)


PvdServiceDep = Annotated[PvdService, Depends(get_pvd_service)]


def get_venda_repository(db: SessionDep) -> VendaRepository:
    return VendaRepository(db)


def get_venda_service(
    repo: Annotated[VendaRepository, Depends(get_venda_repository)],
    repoProducao: Annotated[ProductionRepository, Depends(get_production_repository)],
    repoCliente: Annotated[ClienteRepository, Depends(get_client_repository)],
    repoPvd: Annotated[PvdRepository, Depends(get_pvd_repository)],
) -> VendaService:
    return VendaService(repo, repoProducao, repoCliente, repoPvd)


VendaServiceDep = Annotated[VendaService, Depends(get_venda_service)]
