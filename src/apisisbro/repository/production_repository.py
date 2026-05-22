from collections.abc import Sequence
from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apisisbro.models.models import Insumo, Producao, Produto
from apisisbro.repository.base_repository import BaseRepository


class ProductionRepository(BaseRepository[Producao]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Producao]:
        return Producao

    async def get_estoque_por_ids(self, ids: list[int]) -> Sequence[Insumo]:
        result = await self.session.execute(select(Insumo).where(Insumo.id.in_(ids)))
        return result.scalars().all()

    async def get_production_today(self, data_hoje: date):
        query = (
            select(func.count())
            .select_from(Producao)
            .where(cast(Producao.fabricacao, Date) == data_hoje)
        )

        total = await self.session.scalar(query)

        return total

    async def create(self, producao: Producao) -> Producao:
        self.session.add(producao)
        await self.session.flush()
        query = (
            select(Producao)
            .options(selectinload(Producao.produto).selectinload(Produto.formulas))
            .where(Producao.id == producao.id)
        )
        result = await self.session.scalar(query)
        return result

    async def update_production(self, producao: Producao) -> Producao:
        await self.session.flush()

        query = (
            select(Producao)
            .options(selectinload(Producao.produto).selectinload(Produto.formulas))
            .where(Producao.id == producao.id)
        )

        result = await self.session.scalar(query)

        return result
