from datetime import date
from decimal import Decimal
from http import HTTPStatus

from fastapi import HTTPException

from apisisbro.models.models import Producao
from apisisbro.repository import ProductionRepository, ProductRepository
from apisisbro.schemas.producao_schema import ProducaoCreate


class ProductionService:
    def __init__(self, repo: ProductionRepository, repoProduct: ProductRepository):

        self.repo = repo
        self.repoProduct = repoProduct

    async def create(self, payload: ProducaoCreate, user_id: int) -> Producao:

        produto = await self.repoProduct.get_by_id_with_formulas(payload.produto_id)

        if produto is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Produto não encontrado'
            )

        custo_total = await self._validar_e_abater_estoque(
            produto.formulas, payload.quantidade
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

    async def _validar_e_abater_estoque(self, formulas, quantidade_produzida: int):

        insumos_calculados = {}

        for item in formulas:
            qtd_necessaria = item.quantidade_necessaria
            insumos_calculados[item.insumo_id] = quantidade_produzida * qtd_necessaria

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

            if qtd_necessaria > insumo_obj.quantidade_estoque:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f'Estoque insuficiente para o insumo ID {insumo_id}. '
                    f'Necessário: {qtd_necessaria},'
                    f'Disponível: {insumo_obj.quantidade_estoque}',
                )

            custo_insumo = insumo_obj.custo_unitario * Decimal(qtd_necessaria)
            insumo_obj.quantidade_estoque -= qtd_necessaria
            custo_total_lote += custo_insumo
            await self.repo.update(insumo_obj)
        return custo_total_lote

    async def list_all(self, limit: int = 10, offset: int = 0):
        return await self.repo.get_all(limit, offset)
