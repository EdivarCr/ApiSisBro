from http import HTTPStatus

from fastapi import HTTPException

from apisisbro.models.models import Insumo
from apisisbro.repository.insumo_repository import InsumoRepository
from apisisbro.schemas.producao_schema import (
    InsumoCreate,
    InsumoUpdate,
)


class InsumoService:
    def __init__(
        self,
        repo: InsumoRepository,
    ):
        self.repo = repo

    async def list_all(self):
        return await self.repo.get_all()

    async def create(self, insumoCreate: InsumoCreate) -> Insumo:
        existing = await self.repo.get_insumo_by_name(insumoCreate.nome)

        if existing is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='already exists'
            )
        db_insumo = Insumo(**insumoCreate.model_dump())
        return await self.repo.create(db_insumo)

    async def update(self, insumo_id: int, insumoUpdate: InsumoUpdate) -> Insumo:
        insumo = await self.repo.get_by_id(insumo_id)

        if insumo is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Insumo não econtrado',
            )

        for field, value in insumoUpdate.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(insumo, field, value)

        return await self.repo.update(insumo)

    async def get_by_id(self, insumo_id: int) -> Insumo:
        insumo = await self.repo.get_by_id(insumo_id)

        if insumo is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )

        return insumo

    async def delete(self, insumo_id: int) -> Insumo:
        insumo = await self.repo.get_by_id(insumo_id)

        if insumo is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Insumo nao encontrado'
            )

        return await self.repo.delete(insumo)
