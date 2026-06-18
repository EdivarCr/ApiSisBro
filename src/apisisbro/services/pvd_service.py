from collections.abc import Sequence
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select

from apisisbro.models.models import Cliente, PontoDeVenda
from apisisbro.repository import ClienteRepository, PvdRepository
from apisisbro.schemas.pvd_schema import (
    FilterPontoDeVenda,
    PontoDeVendaCreate,
    PontoDeVendaPaginationResponse,
    PontoDeVendaResponse,
    PontoDeVendaUpdate,
)


class PvdService:
    def __init__(
        self,
        repo: PvdRepository,
    ):
        self.repo = repo

    async def create(self, payload: PontoDeVendaCreate) -> PontoDeVenda:
        query = select(Cliente).where(Cliente.id == payload.id_cliente)
        identifier = await self.repo.session.scalar(query)

        if identifier is None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Nao existe cliente no sistema',
            )

        if identifier.tipo == 'PESSOA_FISICA':
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Nao é possivel criar umm ponto de venda com clientepessoa fisica',
            )

        if payload.google_maps_url:
            query_map = select(PontoDeVenda).where(
                PontoDeVenda.google_maps_url == payload.google_maps_url
            )
            maps_duplicado = await self.repo.session.scalar(query_map)

            if maps_duplicado is not None:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Esta URL do Google Maps ja esta cadastrada',
                )

        new_pvd = PontoDeVenda(**payload.model_dump())
        return await self.repo.create(new_pvd)

    async def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[PontoDeVenda]:
        pvd_list = await self.repo.get_all(limit, offset)
        return {'pvds': pvd_list, 'limit': limit, 'offset': offset}

    async def get_by_filter(self, payload: FilterPontoDeVenda) -> PontoDeVenda:
        filtros_dict = payload.model_dump(exclude_none=True)

        limit = filtros_dict.pop('limit', 10)
        offset = filtros_dict.pop('offset', 0)

        existing = await self.repo.get_all_by_filter(
            filters=filtros_dict,
            like_fields={'name', 'identificador', 'endereco'},
            limit=limit,
            offset=offset,
        )

        if not existing:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Cliente não encontrado com os filtros fornecidos',
            )

        return {'pvds': existing, 'limit': limit, 'offset': offset}

    async def update(self, pvd_id: int, payload: PontoDeVendaUpdate) -> PontoDeVenda:
        pvd = await self.repo.get_by_id(pvd_id)

        if pvd is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(pvd, field, value)

        return await self.repo.update(pvd)

    async def get_by_id(self, pvd_id: int):
        pvd = await self.repo.get_by_id(pvd_id)

        if pvd is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )
        return pvd
