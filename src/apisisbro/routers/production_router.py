from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from apisisbro.core.auth import get_curren_user
from apisisbro.core.dependecies import ProductionServiceDep
from apisisbro.models.models import User
from apisisbro.schemas.producao_schema import (
    ProducaoCreate,
    ProducaoListResponse,
    ProducaoResponse,
    ProducaoUpdate,
)

Current_User = Annotated[
    User,
    Depends(get_curren_user),
]

router = APIRouter(
    prefix='/producao', tags=['producao'], dependencies=[Depends(get_curren_user)]
)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ProducaoResponse)
async def create_production(
    payload: ProducaoCreate,
    usuario_logado: Current_User,
    service: ProductionServiceDep,
):
    return await service.create(payload, usuario_logado.id)


@router.get('/', status_code=HTTPStatus.OK, response_model=ProducaoListResponse)
async def get_producuctions(
    service: ProductionServiceDep,
    limit: int = 10,
    offset: int = 0,
):
    producao = await service.list_all(limit, offset)
    return {'producao': list(producao), 'ofsset': offset, 'limit': limit}


@router.patch('/', status_code=HTTPStatus.OK, response_model=ProducaoResponse)
async def update_production(
    service: ProductionServiceDep, payload: ProducaoUpdate, producao_id: int
):
    return await service.update(payload, producao_id)
