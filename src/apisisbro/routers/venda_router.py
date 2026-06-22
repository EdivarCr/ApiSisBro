from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from apisisbro.core.auth import get_curren_user
from apisisbro.core.dependecies import VendaServiceDep
from apisisbro.models.models import User
from apisisbro.schemas.venda_schema import (
    ListItemVendaResponse,
    ListVendaResponse,
    VendaCreate,
    VendaResponse,
    VendaUpdate,
)

Current_User = Annotated[
    User,
    Depends(get_curren_user),
]


router = APIRouter(
    prefix='/vendas', tags=['venda'], dependencies=[Depends(get_curren_user)]
)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=VendaResponse)
async def create_venda(payload: VendaCreate, service: VendaServiceDep):
    return await service.create(payload)


@router.get('/', status_code=HTTPStatus.OK, response_model=ListVendaResponse)
async def get_all_venda(
    service: VendaServiceDep,
    limit: int = 10,
    offset: int = 0,
):
    return await service.get_all(limit, offset)


@router.get('/{id}', status_code=HTTPStatus.OK, response_model=VendaResponse)
async def get_by_id_venda(id: int, service: VendaServiceDep):
    return await service.get_by_id(id)


@router.put('/{id}', status_code=HTTPStatus.OK, response_model=VendaResponse)
async def update_venda(id: int, payload: VendaUpdate, service: VendaServiceDep):
    return await service.update(id, payload)
