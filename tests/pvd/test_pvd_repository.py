import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import Cliente, PontoDeVenda
from apisisbro.repository.client_repository import ClienteRepository
from apisisbro.repository.pvd_repository import PvdRepository


@pytest.mark.asyncio
async def test_salva_pvd_no_banco(
    session: AsyncSession, cliente_cnpj_factory, pvd_cliente
):
    repo = PvdRepository(session)
    repoClient = ClienteRepository(session)

    cliente_mock = cliente_cnpj_factory.build()
    cliente_salvo = await repoClient.create(cliente_mock)

    pvd_mock = pvd_cliente.build(id_cliente=cliente_salvo.id)
    pvd_salvo = await repo.create(pvd_mock)

    assert pvd_salvo is not None
    assert pvd_salvo.id is not None
    assert cliente_salvo is not None
    assert pvd_salvo.id_cliente == cliente_salvo.id
    assert pvd_salvo.latitude == pvd_mock.latitude


@pytest.mark.asyncio
async def test_get_all_pvds_returns_list(session: AsyncSession, pvd_cliente):
    repo = PvdRepository(session)
    number = 2

    await repo.create(pvd_cliente.build())
    await repo.create(pvd_cliente.build())

    pvds = await repo.get_all()

    assert len(pvds) == number
    assert isinstance(pvds, list)
