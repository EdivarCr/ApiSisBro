import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Cliente
from apisisbro.repository.client_repository import ClienteRepository


@pytest.mark.asyncio
async def test_salva_cliente_no_banco(session: AsyncSession, cliente_cnpj_factory):
    repo = ClienteRepository(session)

    client = cliente_cnpj_factory.build()

    cliente_salvo = await repo.create(client)

    query = select(Cliente).where(Cliente.id == cliente_salvo.id)
    resultado = await session.scalar(query)

    assert resultado is not None
    assert resultado.name == client.name
