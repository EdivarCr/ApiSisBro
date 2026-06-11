from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from apisisbro.core.auth import get_curren_user
from apisisbro.core.dependecies import PvdServiceDep
from apisisbro.models.models import User
from apisisbro.schemas.pvd_schema import (
    FilterPontoDeVenda,
    PontoDeVendaCreate,
    PontoDeVendaPaginationResponse,
    PontoDeVendaResponse,
    PontoDeVendaUpdate,
)

Current_User = Annotated[
    User,
    Depends(get_curren_user),
]

Filter = Annotated[FilterPontoDeVenda, Depends()]

router = APIRouter(prefix='/pvd', tags=['pvd'], dependencies=[Depends(get_curren_user)])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PontoDeVendaResponse)
async def create_pvd(service: PvdServiceDep, payload: PontoDeVendaCreate):
    return await service.create(payload)


@router.get('/', status_code=HTTPStatus.OK, response_model=PontoDeVendaPaginationResponse)
async def list_pvd(
    service: PvdServiceDep,
    limit: int = 10,
    offset: int = 0,
):
    return await service.get_all(limit, offset)


@router.get(
    '/pesquisa', status_code=HTTPStatus.OK, response_model=PontoDeVendaPaginationResponse
)
async def list_pvd_for_filter(
    service: PvdServiceDep,
    payload: Filter,
):
    return await service.get_by_filter(payload)


@router.get('/{pvd_id}', status_code=HTTPStatus.OK, response_model=PontoDeVendaResponse)
async def list_pvd_for_id(
    service: PvdServiceDep,
    pvd_id: int,
):
    return await service.get_by_id(pvd_id)


@router.patch('/{pvd_id}', status_code=HTTPStatus.OK, response_model=PontoDeVendaResponse)
async def update_pvd(service: PvdServiceDep, pvd_id: int, payload: PontoDeVendaUpdate):
    return await service.update(pvd_id, payload)
