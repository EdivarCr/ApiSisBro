from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import EntradaInsumo, Insumo
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.producao_schema import FilterEntradaInsumo


class EntradaInsumoRepository(BaseRepository[EntradaInsumo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[EntradaInsumo]:
        return EntradaInsumo

    async def get_insumo_by_name(self, nome: str) -> EntradaInsumo | None:
        return await self.get_by_name(nome, field='nome')

    async def get_by_filter(self, filter: FilterEntradaInsumo) -> Sequence[EntradaInsumo]:
        query = select(EntradaInsumo).join(Insumo, EntradaInsumo.insumo_id == Insumo.id)

        if filter.insumo_nome is not None:
            query = query.where(Insumo.nome.ilike(f'%{filter.insumo_nome}%'))

        if filter.insumo_tipo is not None:
            query = query.where(Insumo.tipo == filter.insumo_tipo)

        if filter.insumo_ativo is not None:
            query = query.where(Insumo.ativo == filter.insumo_ativo)

        if filter.data_entrada is not None:
            query = query.where(
                func.date(EntradaInsumo.data_entrada) == filter.data_entrada.date()
            )

        result = await self.session.scalars(
            query.offset(filter.offset).limit(filter.limit)
        )
        return result.all()
