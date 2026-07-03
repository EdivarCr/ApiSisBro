from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apisisbro.models.models import Venda, ItemVenda, Produto, ProdutoInsumo
from apisisbro.models.models import ItemVenda, Venda
from apisisbro.repository.base_repository import BaseRepository
from apisisbro.schemas.cliente_schema import ClienteCreate


class VendaRepository(BaseRepository[Venda]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Venda]:
        return Venda

    async def get_all(self, limit: int = 10, offset: int = 0) -> Sequence[Venda]:
        query = (
            select(Venda)
            .options(
                selectinload(Venda.itens)
                .selectinload(ItemVenda.produto)
                .selectinload(Produto.formulas) # Carrega as fórmulas do produto
                .selectinload(ProdutoInsumo.insumo)
            )
            .limit(limit)
            .offset(offset)
            .order_by(Venda.id.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Venda | None:
        query = (
            select(Venda)
            .where(Venda.id == id)
            .options(
                selectinload(Venda.itens)
                .selectinload(ItemVenda.produto)
                .selectinload(Produto.formulas) # Carrega as fórmulas do produto
                .selectinload(ProdutoInsumo.insumo)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all_by_filter(
        self,
        filters: Mapping[str, Any],
        *,
        like_fields: set[str] | None = None,
        limit: int = 10,
        offset: int = 0,
        data_inicio=None,
        data_fim=None,
        **kwargs,
    ) -> Sequence[Venda]:
        
        query = select(self.model).options(
            selectinload(Venda.itens)
            .selectinload(ItemVenda.produto)
            .selectinload(Produto.formulas) # Carrega as fórmulas do produto
            .selectinload(ProdutoInsumo.insumo)
        )
        like_fields = like_fields or set()

        if data_inicio:
            query = query.where(self.model.data_venda >= data_inicio)
        if data_fim:
            query = query.where(self.model.data_venda <= data_fim)

        for field, value in filters.items():
            if value is None:
                continue
            if not hasattr(self.model, field):
                raise AttributeError(
                    f"{self.model.__name__} não possui o campo '{field}'"
                )

            column = getattr(self.model, field)
            if field in like_fields and isinstance(value, str):
                query = query.where(column.ilike(f'%{value}%'))
            else:
                query = query.where(column == value)

        query = query.order_by(self.model.id.desc())

        result = await self.session.scalars(query.offset(offset).limit(limit))
        return result.all()

    async def get_venda_with_items_and_products(self, id: int) -> Venda | None:
        query = (
            select(Venda)
            .where(Venda.id == id)
            .options(selectinload(Venda.itens).selectinload(ItemVenda.produto))
        )
        result = await self.session.execute(query)
        return result.scalars().first()
