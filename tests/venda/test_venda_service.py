from datetime import date, timedelta
from decimal import Decimal
from http import HTTPStatus

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import (
    FormaPagamento,
    ItemVenda,
    Producao,
    StatusPagamento,
    TipoZona,
    Venda,
)
from apisisbro.repository import (
    ClienteRepository,
    ItemVendaRepository,
    ProductionRepository,
    PvdRepository,
    VendaRepository,
)
from apisisbro.schemas.pvd_schema import PontoDeVendaCreate
from apisisbro.schemas.venda_schema import (
    FilterVenda,
    ItemVendaCreate,
    TipoVenda,
    VendaCreate,
    VendaUpdate,
)
from apisisbro.services import VendaService


@pytest.mark.asyncio
async def test_deve_criar_venda_com_sucesso(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
) -> Venda:
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()

    cliente_salvo = await clienteRepo.create(cliente)

    produto1 = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper',
        preco_varejo=Decimal('35.00'),
    )

    produto2 = produto_factory.build(
        criador_id=user.id, nome='Molho Defumado', preco_varejo=Decimal('28.00')
    )

    session.add_all([produto1, produto2])
    await session.flush()

    lote1 = Producao(
        codigo_lote='LOT-REAPER-01',
        produto_id=produto1.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,  # Saldo suficiente para a venda de 2 unidades
    )

    lote2 = Producao(
        codigo_lote='LOT-DEFUMADO-01',
        produto_id=produto2.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=5,  # Saldo suficiente para a venda de 1 unidade
    )

    session.add_all([lote1, lote2])
    await session.flush()

    nova_venda = Venda(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        valor_total=Decimal('98.00'),
        data_venda=date.today(),
        data_pagamento=date.today(),
    )

    item1 = ItemVenda(
        produto_id=produto1.id,
        quantidade=2,
        preco_unitario=Decimal('35.00'),
        subtotal=Decimal('70.00'),
    )
    item2 = ItemVenda(
        produto_id=produto2.id,
        quantidade=1,
        preco_unitario=Decimal('28.00'),
        subtotal=Decimal('28.00'),
    )

    nova_venda.itens = [item1, item2]
    response = await service.create(nova_venda)

    await session.commit()

    # Asserção direta e limpa!
    assert response is not None, 'A venda não foi persistida no banco de dados.'
    assert response.id is not None, 'O ID da venda retornou como None.'
    assert response.valor_total == Decimal('98.00')
    number_lote1 = 8
    number_lote2 = 4

    assert lote1.quantidade == number_lote1
    assert lote2.quantidade == number_lote2


@pytest.mark.asyncio
async def test_deve_buscar_todas_as_vendas_com_sucesso(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 2',
        preco_varejo=Decimal('35.00'),
    )
    session.add(produto)
    await session.flush()

    lote = Producao(
        codigo_lote='LOT-REAPER-02',
        produto_id=produto.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote)
    await session.flush()

    nova_venda = Venda(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        valor_total=Decimal('35.00'),
        data_venda=date.today(),
        data_pagamento=date.today(),
    )
    item = ItemVenda(
        produto_id=produto.id,
        quantidade=1,
        preco_unitario=Decimal('35.00'),
        subtotal=Decimal('35.00'),
    )
    nova_venda.itens = [item]
    await service.create(nova_venda)
    await session.commit()

    # Now get all sales
    result = await service.get_all(limit=10, offset=0)
    assert 'itens' in result
    assert len(result['itens']) >= 1
    number_limit = 10
    number_offset = 0
    assert result['limit'] == number_limit
    assert result['offset'] == number_offset


@pytest.mark.asyncio
async def test_deve_criar_venda_com_desconto_em_porcentagem(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
):

    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 3',
        preco_varejo=Decimal('50.00'),
    )
    session.add(produto)
    await session.flush()

    lote = Producao(
        codigo_lote='LOT-REAPER-03',
        produto_id=produto.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote)
    await session.flush()

    payload = VendaCreate(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('10.00'),  # 10% discount
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto.id,
                quantidade=2,  # 2 * 50.00 = 100.00 subtotal
            )
        ],
    )

    response = await service.create(payload)
    await session.commit()

    assert response is not None
    assert response.valor_subtotal == Decimal('100.00')
    assert response.valor_desconto == Decimal('10.00')  # 10% of 100.00 = 10.00
    assert response.valor_total == Decimal('90.00')  # 100.00 - 10.00 = 90.00


@pytest.mark.asyncio
async def test_deve_devolver_404_ao_buscar_venda_inexistente(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 5',
        preco_varejo=Decimal('50.00'),
    )
    session.add(produto)
    await session.flush()

    lote = Producao(
        codigo_lote='LOT-REAPER-05',
        produto_id=produto.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote)
    await session.flush()

    payload = VendaCreate(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('10.00'),  # 10% discount
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto.id,
                quantidade=2,  # 2 * 50.00 = 100.00 subtotal
            )
        ],
    )

    response = await service.create(payload)
    await session.commit()

    assert response is not None
    assert response.valor_subtotal == Decimal('100.00')
    assert response.valor_desconto == Decimal('10.00')  # 10% of 100.00 = 10.00
    assert response.valor_total == Decimal('90.00')  # 100.00 - 10.00 = 90.00

    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(9999)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == 'Venda nao encontrada'


@pytest.mark.asyncio
async def test_deve_retornar_400_quando_produto_nao_tem_estoque_suficiente(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 6',
        preco_varejo=Decimal('50.00'),
    )
    session.add(produto)
    await session.flush()

    lote = Producao(
        codigo_lote='LOT-REAPER-06',
        produto_id=produto.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote)
    await session.flush()

    payload = VendaCreate(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('10.00'),
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto.id,
                quantidade=11,
            )
        ],
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(payload)
    await session.commit()

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == (
        f'Estoque insuficiente do produto {produto.id}.Disponível: 10 unidades.'
    )


@pytest.mark.asyncio
async def test_deve_retornar_400_quando_produto_nao_tem_lote_cadastrado(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 7',
        preco_varejo=Decimal('50.00'),
    )
    session.add(produto)
    await session.flush()

    payload = VendaCreate(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('10.00'),
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto.id,
                quantidade=2,
            )
        ],
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(payload)
    await session.commit()

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == (
        f'O produto ID {produto.id}não está disponível para venda (sem estoque/lotes).'
    )


@pytest.mark.asyncio
async def test_deve_atualizar_venda_com_sucesso(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
    pvd_cliente,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    repo_pvd = PvdRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
        repoPvd=repo_pvd,
    )
    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)
    pvd = pvd_cliente.build(id_cliente=cliente_salvo.id)
    pvd_salvo = await repo_pvd.create(pvd)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 8',
        preco_varejo=Decimal('50.00'),
    )
    session.add(produto)
    await session.flush()

    lote = Producao(
        codigo_lote='LOT-REAPER-08',
        produto_id=produto.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote)
    await session.flush()

    payload_create = VendaCreate(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=None,
        status_pagamento=StatusPagamento.PENDENTE,
        desconto=Decimal('0.00'),
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto.id,
                quantidade=2,
            )
        ],
    )

    venda_criada = await service.create(payload_create)
    await session.commit()

    assert venda_criada.status_pagamento == StatusPagamento.PENDENTE
    assert venda_criada.forma_pagamento is None

    cliente_2 = cliente_cnpj_factory.build()
    cliente_salvo2 = await clienteRepo.create(cliente_2)

    payload_update = VendaUpdate(
        status_pagamento=StatusPagamento.PAGO,
        forma_pagamento=FormaPagamento.PIX,
        data_pagamento=date.today(),
        cliente_id=cliente_salvo2.id,
        tipo_venda='VAREJO',
        pvd_id=pvd_salvo.id,
    )

    venda_atualizada = await service.update(venda_criada.id, payload_update)
    await session.commit()

    assert venda_atualizada.status_pagamento == StatusPagamento.PAGO
    assert venda_atualizada.forma_pagamento == FormaPagamento.PIX
    assert venda_atualizada.data_pagamento == date.today()


@pytest.mark.asyncio
async def test_deve_retornar_404_ao_atualizar_venda_inexistente(
    session: AsyncSession,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    payload_update = VendaUpdate(
        status_pagamento=StatusPagamento.PAGO,
        forma_pagamento=FormaPagamento.PIX,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.update(9999, payload_update)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == 'Venda nao encontrada'


@pytest.mark.asyncio
async def test_deve_atualizar_desconto_da_venda_e_recalcular_valores(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    service = VendaService(
        repo=repo,
        repoPoducao=producao,
        repoCliente=clienteRepo,
    )

    cliente = cliente_cnpj_factory.build()
    cliente_salvo = await clienteRepo.create(cliente)

    produto = produto_factory.build(
        criador_id=user.id,
        nome='Carolina Reaper 9',
        preco_varejo=Decimal('50.00'),
    )
    session.add(produto)
    await session.flush()

    lote = Producao(
        codigo_lote='LOT-REAPER-09',
        produto_id=produto.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote)
    await session.flush()

    payload_create = VendaCreate(
        cliente_id=cliente_salvo.id,
        pvd_id=None,
        tipo_venda='VAREJO',
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('0.00'),
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto.id,
                quantidade=2,
            )
        ],
    )

    venda_criada = await service.create(payload_create)
    await session.commit()

    assert venda_criada.valor_subtotal == Decimal('100.00')
    assert venda_criada.valor_desconto == Decimal('0.00')
    assert venda_criada.valor_total == Decimal('100.00')

    payload_update = VendaUpdate(
        desconto=Decimal('20.00'),
    )

    venda_atualizada = await service.update(venda_criada.id, payload_update)
    await session.commit()

    assert venda_atualizada.valor_subtotal == Decimal('100.00')
    assert venda_atualizada.valor_desconto == Decimal('20.00')
    assert venda_atualizada.valor_total == Decimal('80.00')


@pytest.mark.asyncio
async def test_deve_listar_com_filter(
    session: AsyncSession,
    cliente_cnpj_factory,
    produto_factory,
    user,
    pvd_cliente,
):
    repo = VendaRepository(session)
    producao = ProductionRepository(session)
    clienteRepo = ClienteRepository(session)
    pvdRepo = PvdRepository(session)
    service = VendaService(
        repo=repo, repoPoducao=producao, repoCliente=clienteRepo, repoPvd=pvdRepo
    )

    cliente1 = cliente_cnpj_factory.build()
    cliente2 = cliente_cnpj_factory.build()
    cliente1_salvo = await clienteRepo.create(cliente1)
    cliente2_salvo = await clienteRepo.create(cliente2)

    produto1 = produto_factory.build(
        criador_id=user.id, nome='Carolina Reaper 10', preco_varejo=Decimal('50.00')
    )
    produto2 = produto_factory.build(
        criador_id=user.id, nome='Carolina Reaper 11', preco_varejo=Decimal('60.00')
    )
    pvd = pvd_cliente.build(id_cliente=cliente1_salvo.id)
    pvd2 = pvd_cliente.build(id_cliente=cliente2_salvo.id)
    pvd_salvo = await pvdRepo.create(pvd)
    pvd2_salvo = await pvdRepo.create(pvd2)

    session.add(produto1)
    session.add(produto2)
    await session.flush()

    lote1 = Producao(
        codigo_lote='LOT-REAPER-10',
        produto_id=produto1.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    lote2 = Producao(
        codigo_lote='LOT-REAPER-11',
        produto_id=produto2.id,
        criado_por_id=user.id,
        validade=date.today() + timedelta(days=180),
        quantidade=10,
    )
    session.add(lote1)
    session.add(lote2)
    await session.flush()

    payload_create1 = VendaCreate(
        cliente_id=cliente1_salvo.id,
        pvd_id=pvd_salvo.id,
        tipo_venda=TipoVenda.ATACADO,
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('0.00'),
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto1.id,
                quantidade=1,
            ),
            ItemVendaCreate(
                produto_id=produto2.id,
                quantidade=1,
            ),
        ],
    )

    payload_create2 = VendaCreate(
        cliente_id=cliente2_salvo.id,
        pvd_id=pvd2_salvo.id,
        tipo_venda=TipoVenda.ATACADO,
        forma_pagamento=FormaPagamento.PIX,
        status_pagamento=StatusPagamento.PAGO,
        desconto=Decimal('0.00'),
        data_venda=date.today(),
        itens=[
            ItemVendaCreate(
                produto_id=produto1.id,
                quantidade=1,
            ),
            ItemVendaCreate(
                produto_id=produto2.id,
                quantidade=1,
            ),
        ],
    )

    await service.create(payload_create1)
    await service.create(payload_create2)
    await session.commit()

    payload_filter = FilterVenda(
        data_inicio=date.today(),
        data_fim=date.today(),
        status_pagamento=StatusPagamento.PAGO,
        pvd_id=None,
        cliente_id=None,
        forma_pagamento=FormaPagamento.PIX,
        tipo_venda=TipoVenda.ATACADO,
    )

    vendas_filtradas = await service.filtro_vendas(payload_filter)
    number = 2
    assert len(vendas_filtradas['itens']) == number
