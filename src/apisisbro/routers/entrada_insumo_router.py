from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from apisisbro.core.auth import get_curren_user
from apisisbro.core.dependecies import EntradaInsumoServideDep
from apisisbro.models.models import User
from apisisbro.schemas.producao_schema import (
    EntradaInsumoCreate,
    EntradaInsumoListResponse,
    EntradaInsumoResponse,
    FilterEntradaInsumo,
)

Current_User = Annotated[
    User,
    Depends(get_curren_user),
]

Filter = Annotated[FilterEntradaInsumo, Depends()]

router = APIRouter(
    prefix='/entrada_insumo',
    tags=['entrada_insumo'],
    dependencies=[Depends(get_curren_user)],
)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=EntradaInsumoResponse)
async def crete_entrada_insumo(
    entradaInsumoCreate: EntradaInsumoCreate,
    service: EntradaInsumoServideDep,
    usuario_logado: Current_User,
):
    return await service.registrar_entrada(entradaInsumoCreate, usuario_logado.id)


@router.get('/', status_code=HTTPStatus.OK, response_model=EntradaInsumoListResponse)
async def get_all_entradas_insumo(
    service: EntradaInsumoServideDep,
    limit: int = 10,
    offset: int = 0,
):
    entradas = await service.get_all_entrada_insumo(limit=limit, offset=offset)
    return {
        'entradaInsumo': list(entradas),
        'offset': offset,
        'limit': limit,
    }


@router.get(
    '/entrada_insumo_id',
    status_code=HTTPStatus.OK,
    response_model=EntradaInsumoResponse,
)
async def get_entrada_insumo(service: EntradaInsumoServideDep, entrada_id: int):
    return await service.get_entrada_insumo_by_id(entrada_id)


@router.delete('/{entrada_insumo_id}', status_code=HTTPStatus.NO_CONTENT)
async def estornar_entra_insumo(
    entrada_insumo_id: int,
    service: EntradaInsumoServideDep,
):
    try:
        return await service.delete(entrada_insumo_id)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e)) from e


@router.get(
    '/pesquisa', status_code=HTTPStatus.OK, response_model=EntradaInsumoListResponse
)
async def search_entrada_insumo(service: EntradaInsumoServideDep, filter: Filter):
    entradas = await service.list_by_filter(filter)
    return {
        'entradaInsumo': list(entradas),
        'offset': filter.offset,
        'limit': filter.limit,
    }
