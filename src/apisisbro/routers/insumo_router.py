from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from apisisbro.core.auth import get_curren_user
from apisisbro.core.dependecies import InsumoServiceDep
from apisisbro.models.models import User
from apisisbro.schemas.producao_schema import InsumoCreate, InsumoResponse, InsumoUpdate

Current_User = Annotated[
    User,
    Depends(get_curren_user),
]

router = APIRouter(
    prefix='/insumos', tags=['insumo'], dependencies=[Depends(get_curren_user)]
)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=InsumoResponse)
async def create_insumo(
    service: InsumoServiceDep,
    insumoCreate: InsumoCreate,
):
    try:
        return await service.create(insumoCreate)
    except SyntaxError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Erro ao criar insumo'
        ) from e


@router.patch(
    '/{insumo_id}', status_code=HTTPStatus.OK, response_model=InsumoResponse
)
async def update_insumo(
    insumo_id: int,
    service: InsumoServiceDep,
    insumoUpdate: InsumoUpdate
    ):
    return await service.update(insumo_id, insumoUpdate)


@router.get('/all', response_model=list[InsumoResponse])
async def get_all_insumo(service: InsumoServiceDep):
    return await service.list_all()


@router.get('/{insumo_id}', response_model=InsumoResponse)
async def get_insumo_by_id(insumo_id: int, service: InsumoServiceDep):
    return await service.get_by_id(insumo_id)
