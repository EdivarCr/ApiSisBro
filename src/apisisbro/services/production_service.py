from datetime import date
from decimal import Decimal
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Producao
from apisisbro.repository import ProductionRepository, ProductRepository
from apisisbro.schemas.producao_schema import ProducaoCreate, ProducaoUpdate


class ProductionService:
    def __init__(
        self, repo: ProductionRepository,
        repoProduct: ProductRepository,
        repoDb: AsyncSession
    ):

        self.repo = repo
        self.repoProduct = repoProduct
        self.repoDb = repoDb

    async def create(self, payload: ProducaoCreate, user_id: int) -> Producao:

        produto = await self.repoProduct.get_by_id_with_formulas(payload.produto_id)

        if produto is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Produto não encontrado'
            )

        custo_total = await self._validar_e_abater_estoque(
            produto.formulas,
            payload.quantidade,
        )

        codigo_lote = await self.create_codigo()
        custo_unitario = custo_total / payload.quantidade
        nova_producao = Producao(
            produto_id=payload.produto_id,
            quantidade=payload.quantidade,
            codigo_lote=codigo_lote,
            criado_por_id=user_id,
            validade=payload.validade,
            custo_total=custo_total,
            custo_unitario=custo_unitario,
        )

        return await self.repo.create(nova_producao)

    async def create_codigo(self):
        data_hoje_str = date.today()

        contador = await self.repo.get_production_today(data_hoje_str)

        sequencial = contador + 1

        codigo_lote = f'{data_hoje_str}-{sequencial:03d}'
        return codigo_lote

    async def _validar_e_abater_estoque(
        self,
        formulas,
        delta_quantidade: int,
        nova_quantidade: int | None = None,
    ):

        if delta_quantidade == 0:
            return Decimal('0.00')

        insumos_calculados = {}

        for item in formulas:
            total_necessairo = item.quantidade_necessaria * delta_quantidade
            insumos_calculados[item.insumo_id] = total_necessairo

        ids_necessarios = list(insumos_calculados.keys())
        # IMPORTANTE: Garanta que esse método do repo retorne os OBJETOS Insumo inteiros
        estoque_db = await self.repo.get_estoque_por_ids(ids_necessarios)
        mapa_estoque = {item.id: item for item in estoque_db}  # Guarda o OBJETO

        custo_total_lote = Decimal('0.00')

        # Valida e abate
        for insumo_id, qtd_necessaria in insumos_calculados.items():
            insumo_obj = mapa_estoque.get(insumo_id)

            if not insumo_obj:
                raise HTTPException(
                    status_code=400, detail=f'Insumo ID {insumo_id} não cadastrado.'
                )

            if qtd_necessaria > 0:
                if qtd_necessaria > insumo_obj.quantidade_estoque:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f'Estoque insuficiente para o insumo ID {insumo_id}. '
                        f'Necessário: {qtd_necessaria},'
                        f'Disponível: {insumo_obj.quantidade_estoque}',
                    )

            insumo_obj.quantidade_estoque -= qtd_necessaria
            item_formula = next(f for f in formulas if f.insumo_id == insumo_id)
            qtd_total_necessaria = delta_quantidade * item_formula.quantidade_necessaria
            custo_insumo = insumo_obj.custo_unitario * Decimal(qtd_total_necessaria)
            custo_total_lote += custo_insumo

            await self.repoDb.flush()

        return custo_total_lote

    async def list_all(self, limit: int = 10, offset: int = 0):
        return await self.repo.get_all(limit, offset)

    async def update(self, payload: ProducaoUpdate, producao_id: int) -> Producao:
        production = await self.repo.get_by_id(producao_id)

        if production is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Producao nao encontrada'
            )

        if payload.validade is not None:
            validade_final = payload.validade
        else:
            validade_final = production.validade

        if production.fabricacao and validade_final:
            if validade_final < production.fabricacao.date():
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail='A data de validade não pode ser anterior àdata de fabricação',
                )
            production.validade = validade_final

        if payload.quantidade is not None:
            delta_quantidade = payload.quantidade - production.quantidade

            if delta_quantidade != 0:
                product = await self.repoProduct.get_by_id_with_formulas(
                    production.produto_id
                    )
                custo_delta = await self._validar_e_abater_estoque(
                    product.formulas, delta_quantidade, payload.quantidade
                )

                production.quantidade = payload.quantidade
                production.custo_total = custo_delta
                quantidade_total = Decimal(payload.quantidade)
                production.custo_unitario = production.custo_total / quantidade_total

        if payload.status is not None:
            production.status = payload.status

        return await self.repo.update_production(production)
