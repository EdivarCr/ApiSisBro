from http import HTTPStatus

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import TipoZona
from apisisbro.repository import ClienteRepository, PvdRepository
from apisisbro.schemas.pvd_schema import PontoDeVendaCreate
from apisisbro.services import PvdService


@pytest.mark.asyncio
async def test_deve_lancar_erro_se_identificador_ja_existir_naquela_zona(
    session: AsyncSession,
    cliente_cnpj_factory,
    pvd_cliente,
):

    repoCliente = ClienteRepository(session)
    repo = PvdRepository(session)
    service = PvdService(repo)

    cliente_mock = cliente_cnpj_factory.build()
    cliente_salvo = await repoCliente.create(cliente_mock)

    url_duplicda = 'https://maps.google.com/exemplo_pvd'
    zona_duplicada = TipoZona.ZONA_NORTE

    pvd_mock1 = pvd_cliente.build(
        id_cliente=cliente_salvo.id,
        google_maps_url=url_duplicda,
        tipo_zona=zona_duplicada,
    )

    payload1 = PontoDeVendaCreate(**pvd_mock1.__dict__)
    await service.create(payload1)

    pvd2_mock = pvd_cliente.build(
        id_cliente=cliente_salvo.id,
        google_maps_url=url_duplicda,
        tipo_zona=zona_duplicada,
    )
    payload2 = PontoDeVendaCreate(**pvd2_mock.__dict__)
    with pytest.raises(HTTPException) as exc_info:
        await service.create(payload2)

    assert exc_info.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_cria_pvd(
    session: AsyncSession,
    cliente_cnpj_factory,
    pvd_cliente,
):

    repoCliente = ClienteRepository(session)
    repo = PvdRepository(session)
    service = PvdService(repo)

    cliente_mock = cliente_cnpj_factory.build()
    cliente_salvo = await repoCliente.create(cliente_mock)

    pvd_mock = pvd_cliente.build(id_cliente=cliente_salvo.id)
    pvd_salvo = PontoDeVendaCreate(**pvd_mock.__dict__)
    resultado = await service.create(pvd_salvo)

    assert resultado is not None
    assert resultado.id is not None
    assert resultado.id_cliente == cliente_salvo.id


@pytest.mark.asyncio
async def test_listar_todos_pvds(
    session: AsyncSession,
    cliente_cnpj_factory,
    pvd_cliente,
):
    repoCliente = ClienteRepository(session)
    repo = PvdRepository(session)
    service = PvdService(repo)
    number = 3
    cliente_mock = cliente_cnpj_factory.build()
    cliente_salvo = await repoCliente.create(cliente_mock)

    payloads = [
        PontoDeVendaCreate(**pvd_cliente.build(id_cliente=cliente_salvo.id).__dict__),
        PontoDeVendaCreate(**pvd_cliente.build(id_cliente=cliente_salvo.id).__dict__),
        PontoDeVendaCreate(**pvd_cliente.build(id_cliente=cliente_salvo.id).__dict__),
    ]

    for payload in payloads:
        await service.create(payload)

    lista_pvds = await service.get_all()

    assert lista_pvds is not None
    assert len(lista_pvds['pvds']) == number
