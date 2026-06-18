from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import FormaPagamento, ItemVenda, StatusPagamento, Venda
from apisisbro.repository import ClienteRepository, ItemVendaRepository, VendaRepository


@pytest.mark.asyncio
async def test_salva_venda_no_banco(
    session: AsyncSession, cliente_cnpj_factory, pvd_cliente, produto_factory, user
):

    repo = VendaRepository(session)
    repoCliente = ClienteRepository(session)

    cliente = cliente_cnpj_factory.build()

    cliente_salvo = await repoCliente.create(cliente)

    produto1 = produto_factory.build(
        criador_id=user.id, nome='Carolina Reaper', preco_varejo=Decimal('35.00')
    )
    produto2 = produto_factory.build(
        criador_id=user.id, nome='Molho Defumado', preco_varejo=Decimal('28.00')
    )

    session.add_all([produto1, produto2])
    await session.flush()

    # 4. Instancia a venda mãe normalmente
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

    # 5. Instancia os itens com os IDs garantidos
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

    # 6. Associa em memória e manda o repositório salvar tudo junto
    nova_venda.itens = [item1, item2]

    await repo.create(nova_venda)
    await session.flush()
    await session.commit()  # <--- O único commit do teste, bem no final!

    venda_salva = await repo.get_by_id(nova_venda.id)
    number = 2
    assert venda_salva is not None
    assert venda_salva.valor_total == Decimal('98.00')
    await session.refresh(venda_salva, ['itens'])
    assert len(venda_salva.itens) == number
