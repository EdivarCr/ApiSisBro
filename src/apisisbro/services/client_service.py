from collections.abc import Sequence
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select

from apisisbro.models.models import Cliente
from apisisbro.repository import ClienteRepository
from apisisbro.schemas.cliente_schema import (
    ClienteCreate,
    ClienteUpdate,
    FilterClienteResponse,
)


class ClientService:
    def __init__(
        self,
        repo: ClienteRepository,
    ):
        self.repo = repo

    async def create(self, payload: ClienteCreate):
        query = select(Cliente).where(Cliente.identificador == payload.identificador)
        identifier = await self.repo.session.scalar(query)

        if identifier:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='um cliente com este CPF/CNPJ já está cadastrado',
            )

        new_client = Cliente(**payload.model_dump())
        return await self.repo.create(new_client)

    async def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[Cliente]:
        costumers_list = await self.repo.get_all(limit, offset)
        return {'costumers': costumers_list, 'limit': limit, 'offset': offset}

    async def get_by_id(self, client_id: int) -> Cliente:
        client = await self.repo.get_by_id(client_id)

        if client is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )

        return client

    async def get_by_filter(self, payload: FilterClienteResponse) -> Cliente:
        filtros_dict = payload.model_dump(exclude_none=True)

        limit = filtros_dict.pop('limit', 10)
        offset = filtros_dict.pop('offset', 0)

        existing = await self.repo.get_all_by_filter(
            filters=filtros_dict,
            like_fields={'name', 'identificador', 'endereco'},
            limit=limit,
            offset=offset,
        )

        return {
            'costumers': existing if existing else [],
            'limit': limit,
            'offset': offset
        }
        if not existing:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Cliente não encontrado com os filtros fornecidos',
            )

        return existing

    async def update(self, client_id: int, payload: ClienteUpdate) -> Cliente:
        client = await self.repo.get_by_id(client_id)

        if client is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='produto nao encontrado',
            )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(client, field, value)

        return await self.repo.update(client)
