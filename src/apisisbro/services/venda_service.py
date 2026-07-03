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
from apisisbro.schemas.venda_schema import FilterVenda, VendaCreate, VendaUpdate, ProdutoLucroKPI


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

    async def get_dashboard_geral(self, data_inicio: date | None = None, data_fim: date | None = None) -> dict:
        """
        Calcula os totais financeiros (Faturado, Recebido, Pendente) e o histórico mensal
        para o período selecionado.
        """
        vendas = await self.repo.get_all_by_filter(
            filters={},
            like_fields=set(),
            limit=999999,
            offset=0,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        total_faturado = Decimal("0.00")
        total_recebido = Decimal("0.00")
        total_pendente = Decimal("0.00")
        
        atacado = Decimal("0.00")
        varejo = Decimal("0.00")

        # Dicionário temporário para agrupar faturamento por mês (Ano-Mês)
        por_mes = {}
        produtos_dict = {}

        for v in vendas:
            # Ignora vendas canceladas nos cálculos de faturamento
            if v.status_pagamento == 'CANCELADO':
                continue
                
            valor = Decimal(str(v.valor_total))
            total_faturado += valor
            
            if v.status_pagamento == 'PAGO':
                total_recebido += valor
            elif v.status_pagamento == 'PENDENTE':
                total_pendente += valor

            if v.tipo_venda == 'ATACADO':
                atacado += valor
            elif v.tipo_venda == 'VAREJO':
                varejo += valor
            
            for item in v.itens:
                produto = getattr(item, 'produto', None)
                nome = produto.nome if produto else f"Produto #{item.produto_id}"
                
                produtos_dict[nome] = produtos_dict.get(nome, 0) + item.quantidade
            
            # Agrupamento mensal para os gráficos
            mes_chave = v.data_venda.strftime("%Y-%m")
            if mes_chave not in por_mes:
                por_mes[mes_chave] = {"faturamento": Decimal("0.00"), "qtd": 0}
            por_mes[mes_chave]["faturamento"] += valor
            por_mes[mes_chave]["qtd"] += 1

        # Formata o gráfico mensal para a resposta do endpoint
        faturamento_por_mes = [
            {"mes": k, "faturamento": v["faturamento"], "quantidade_vendas": v["qtd"]}
            for k, v in sorted(por_mes.items())
        ]

        proporcao_vendas = [
            {"tipo": "Atacado", "valor": atacado},
            {"tipo": "Varejo", "valor": varejo}
        ]

        ranking_produtos = sorted(produtos_dict.items(), key=lambda x: x[1], reverse=True)
        produtos_mais_vendidos = []
        for nome, qtd in produtos_dict.items():
            prod_kpi = ProdutoLucroKPI(
                produto_id=0,
                nome_produto=nome,
                quantidade_vendida=qtd,
                faturamento_total=Decimal("0.00"),
                custo_total=Decimal("0.00"), 
                lucro_total=Decimal("0.00"),
                margem_lucro=Decimal("0.00")
            )
            produtos_mais_vendidos.append(prod_kpi)

        return {
            "total_faturado": total_faturado,
            "total_recebido": total_recebido,
            "total_pendente": total_pendente,
            "quantidade_vendas": len([v for v in vendas if v.status_pagamento != 'CANCELADO']),
            "faturamento_por_mes": faturamento_por_mes,
            "proporcao_vendas": proporcao_vendas,
            "produtos_mais_vendidos": produtos_mais_vendidos
        }

    async def get_dashboard_lucratividade(self, data_inicio: date | None = None, data_fim: date | None = None) -> dict:
        """
        Cruza as vendas com o preço de custo dos itens para calcular lucro real e margens.
        """
        vendas = await self.repo.get_all_by_filter(
            filters={},
            like_fields=set(),
            limit=999999,
            offset=0,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        faturamento_total = Decimal("0.00")
        custo_total = Decimal("0.00")
        produtos_dict = {}

        atacado = Decimal("0.00")
        varejo = Decimal("0.00")
        for v in vendas:
            if v.status_pagamento == 'CANCELADO':
                continue
            
            for item in v.itens:
                produto = item.produto
                custo_total_produto = Decimal("0.00")
                
                if produto and produto.formulas:
                    for formula in produto.formulas:
                        custo_insumo = formula.insumo.custo_unitario
                        quantidade_usada = formula.quantidade_necessaria
                        custo_total_produto += (custo_insumo * quantidade_usada)

            if v.tipo_venda == 'ATACADO':
                atacado += Decimal(str(v.valor_total))
            elif v.tipo_venda == 'VAREJO':
                varejo += Decimal(str(v.valor_total))

            faturamento_total += Decimal(str(v.valor_total))
            
            # Navega pelos itens da venda para calcular o custo baseado no preço de custo do produto
            for item in v.itens:
                # Caso a relação traga o objeto do produto preenchido pelo ORM
                produto = getattr(item, 'produto', None)
                preco_custo = Decimal(str(custo_total_produto)) if produto else Decimal("0.00")
                
                qtd = item.quantidade
                item_custo_total = preco_custo * qtd
                custo_total += item_custo_total
                
                # Agrupamento por produto para o ranking
                p_id = item.produto_id
                if p_id not in produtos_dict:
                    produtos_dict[p_id] = {
                        "produto_id": p_id,
                        "nome_produto": produto.nome if produto else f"Produto #{p_id}",
                        "quantidade_vendida": 0,
                        "faturamento_total": Decimal("0.00"),
                        "custo_total": Decimal("0.00")
                    }
                
                produtos_dict[p_id]["quantidade_vendida"] += qtd
                produtos_dict[p_id]["faturamento_total"] += Decimal(str(item.subtotal))
                produtos_dict[p_id]["custo_total"] += item_custo_total

        proporcao_vendas = [
            {"tipo": "Atacado", "valor": atacado},
            {"tipo": "Varejo", "valor": varejo}
        ]
        # Calcula margens e lucros por produto individualmente
        ranking_produtos = []
        for p in produtos_dict.values():
            lucro = p["faturamento_total"] - p["custo_total"]
            margem = (lucro / p["faturamento_total"] * 100) if p["faturamento_total"] > 0 else Decimal("0.00")
            
            ranking_produtos.append({
                **p,
                "lucro_total": lucro,
                "margem_lucro": round(margem, 2)
            })

        # Ordena o ranking pelos produtos que geraram mais lucro líquido
        ranking_produtos.sort(key=lambda x: x["lucro_total"], reverse=True)

        lucro_liquido_total = faturamento_total - custo_total
        margem_media = (lucro_liquido_total / faturamento_total * 100) if faturamento_total > 0 else Decimal("0.00")

        return {
            "faturamento_total": faturamento_total,
            "custo_total": custo_total,
            "lucro_liquido_total": lucro_liquido_total,
            "margem_media": round(margem_media, 2),
            "ranking_produtos": ranking_produtos[:10],  # Retorna o Top 10 produtos
            "proporcao_vendas": proporcao_vendas   
        }