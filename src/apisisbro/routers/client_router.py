from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from apisisbro.core.auth import get_curren_user
from apisisbro.core.dependecies import ClientServiceDep
from apisisbro.models.models import User
from apisisbro.schemas.cliente_schema import (
    ClienteCreate,
    ClientePaginationResponse,
    ClienteResponse,
    ClienteUpdate,
    FilterClienteResponse,
)

Current_User = Annotated[
    User,
    Depends(get_curren_user),
]

Filter = Annotated[FilterClienteResponse, Depends()]

router = APIRouter(
    prefix='/clientes', tags=['cliente'], dependencies=[Depends(get_curren_user)]
)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ClienteResponse)
async def create_costumer(service: ClientServiceDep, payload: ClienteCreate):
    return await service.create(payload)


@router.get('/', status_code=HTTPStatus.OK, response_model=ClientePaginationResponse)
async def list_costumer(
    service: ClientServiceDep,
    limit: int = 10,
    offset: int = 0,
):
    return await service.get_all(limit, offset)

@router.get(
    '/pesquisa', status_code=HTTPStatus.OK, response_model=ClientePaginationResponse
)
async def list_costumer_for_filter(service: ClientServiceDep, payload: Filter):
    return await service.get_by_filter(payload)

@router.get('/{client_id}', status_code=HTTPStatus.OK, response_model=ClienteResponse)
async def list_costumer_for_id(
    service: ClientServiceDep,
    client_id: int,
):
    return await service.get_by_id(client_id)

@router.patch(
    '/{client_id}', status_code=HTTPStatus.OK, response_model=ClienteResponse
)
async def update_client(
    service: ClientServiceDep,
    payload: ClienteUpdate,
    client_id: int,
):
    return await service.update(client_id, payload)
