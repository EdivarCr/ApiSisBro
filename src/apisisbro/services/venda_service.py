from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select

from apisisbro.models.models import Cliente, ItemVenda, Producao, Venda
from apisisbro.repository import (
    ClienteRepository,
    ProductionRepository,
    PvdRepository,
    VendaRepository,
)
from apisisbro.schemas.venda_schema import FilterVenda, VendaCreate, VendaUpdate


class VendaService:
    def __init__(
        self,
        repo: VendaRepository,
        repoPoducao: ProductionRepository,
        repoCliente: ClienteRepository,
        repoPvd: PvdRepository,
    ):
        self.repo = repo
        self.repo_producao = repoPoducao
        self.repo_cliente = repoCliente
        self.repo_pvd = repoPvd

    async def create(self, payload: VendaCreate) -> Venda:
        cliente = await self.repo_cliente.get_by_id(payload.cliente_id)
        if cliente is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Cliente nao encontrado'
            )

        itens_venda_processador = []
        valor_total_calculado = Decimal('0.00')
        valor_subtotal = Decimal('0.00')

        for item in payload.itens:
            lotes_ativos = await self.repo_producao.get_lotes_disponiveis_por_produto(
                produto_id=item.produto_id
            )

            if not lotes_ativos:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f'O produto ID {item.produto_id}'
                    'não está disponível para venda (sem estoque/lotes).',
                )

            produto_db = lotes_ativos[0].produto

            if payload.tipo_venda == 'ATACADO':
                preco_unitario = produto_db.preco_atacado
            else:
                preco_unitario = produto_db.preco_varejo

            estoque_total = sum(lote.quantidade for lote in lotes_ativos)

            if estoque_total < item.quantidade:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f'Estoque insuficiente do produto {item.produto_id}.'
                    f'Disponível: {estoque_total} unidades.',
                )

            quantidade_para_abater = item.quantidade

            for lote in lotes_ativos:
                if quantidade_para_abater <= 0:
                    break

                if lote.quantidade >= quantidade_para_abater:
                    lote.quantidade -= quantidade_para_abater
                    quantidade_para_abater = 0
                else:
                    quantidade_para_abater -= lote.quantidade
                    lote.quantidade = 0

            subtotal_item = item.quantidade * preco_unitario
            valor_subtotal += subtotal_item

            novo_item = ItemVenda(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=preco_unitario,
                subtotal=subtotal_item,
            )

            itens_venda_processador.append(novo_item)

        desconto_percentual = getattr(payload, 'desconto', Decimal('0.00')) or Decimal(
            '0.00'
        )
        valor_desconto = (
            valor_subtotal * (desconto_percentual / Decimal('100.00'))
        ).quantize(Decimal('0.01'))
        valor_total_calculado = (valor_subtotal - valor_desconto).quantize(
            Decimal('0.01')
        )

        nova_venda = Venda(
            cliente_id=cliente.id,
            pvd_id=payload.pvd_id,
            tipo_venda=payload.tipo_venda,
            forma_pagamento=payload.forma_pagamento,
            status_pagamento=payload.status_pagamento,
            tipo_conta_destino=payload.tipo_conta_destino,
            valor_subtotal=valor_subtotal,
            valor_desconto=valor_desconto,
            valor_total=valor_total_calculado,
            data_venda=date.today(),
            data_pagamento=date.today() if payload.status_pagamento == 'PAGO' else None,
        )
        nova_venda.itens = itens_venda_processador
        venda_salva = await self.repo.create(nova_venda)

        cliente.total_compras += venda_salva.valor_total
        cliente.quantidade_compras += 1
        cliente.ultima_compra = venda_salva.data_venda

        await self.repo_cliente.update(cliente)

        return await self.get_by_id(venda_salva.id)

    async def get_all(self, limit: int = 10, offset: int = 0) -> dict:
        venda_list = await self.repo.get_all(limit, offset)
        return {'itens': venda_list, 'limit': limit, 'offset': offset}

    async def get_by_id(self, id: int) -> Venda:
        venda = await self.repo.get_by_id(id)
        if venda is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Venda nao encontrada'
            )
        return venda

    async def update(self, id: int, payload: VendaUpdate) -> Venda:
        venda = await self.repo.get_by_id(id)
        if venda is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Venda nao encontrada'
            )

        if payload.cliente_id is not None:
            cliente = await self.repo_cliente.get_by_id(payload.cliente_id)
            if cliente is None:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail='Cliente nao encontrado'
                )
            venda.cliente_id = payload.cliente_id

        if payload.pvd_id is not None:
            pvd = await self.repo_pvd.get_by_id(payload.pvd_id)
            if pvd is None:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail='Ponto de venda nao encontrado',
                )
            venda.pvd_id = payload.pvd_id

        update_data = payload.model_dump(exclude_unset=True)

        if 'desconto' in update_data:
            desconto_percentual = update_data.pop('desconto')
            if desconto_percentual is not None:
                valor_desconto = (
                    venda.valor_subtotal * (desconto_percentual / Decimal('100.00'))
                ).quantize(Decimal('0.01'))
                venda.valor_desconto = valor_desconto
                venda.valor_total = (venda.valor_subtotal - valor_desconto).quantize(
                    Decimal('0.01')
                )

        for field, value in update_data.items():
            setattr(venda, field, value)

        return await self.repo.update(venda)

    async def filtro_vendas(self, filter: FilterVenda) -> dict:
        filter_dict = filter.model_dump(
            exclude={'limit', 'offset', 'data_inicio', 'data_fim'}, exclude_none=True
        )
        result = await self.repo.get_all_by_filter(
            filters=filter_dict,
            like_fields={
                'status_pagamento',
                'forma_pagamento',
                'tipo_venda',
                'cliente_id',
                'pvd_id',
            },
            limit=filter.limit,
            offset=filter.offset,
            data_inicio=filter.data_inicio,
            data_fim=filter.data_fim,
        )

        return {'itens': result, 'limit': filter.limit, 'offset': filter.offset}
