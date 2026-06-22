from http import HTTPStatus

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.repository import ClienteRepository
from apisisbro.schemas.cliente_schema import ClienteCreate, FilterClienteResponse
from apisisbro.services.client_service import ClientService


@pytest.mark.asyncio
async def test_deve_lancar_erro_se_identificador_ja_existir(
    session: AsyncSession,
    cliente_cnpj_factory,
):

    # Dado: Um cliente já cadastrado no banco de dados com um CNPJ específico
    repo = ClienteRepository(session)
    cliente_existente = cliente_cnpj_factory.build(identificador='12.345.678/0001-99')
    await repo.create(cliente_existente)

    # E: Um payload de criação com o MESMO CNPJ
    payload = ClienteCreate(
        name='Outra Loja',
        tipo='COMERCIO',
        identificador='12.345.678/0001-99',  # Conflito aqui
        telefone='85988887777',
        email='outro@email.com',
        endereco='Av Central',
    )

    service = ClientService(repo)

    # Quando / Então: O service deve interceptar e lançar um erro 400 Bad Request
    with pytest.raises(HTTPException) as exc_info:
        await service.create(payload)

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert 'já está cadastrado' in exc_info.value.detail


@pytest.mark.asyncio
async def test_deve_listar_vazio_se_nao_houver_cliente(session: AsyncSession):
    repo = ClienteRepository(session)
    service = ClientService(repo)

    clients = await service.get_all()
    assert len(clients['costumers']) == 0


@pytest.mark.asyncio
async def test_deve_listar_cliente_por_id(session: AsyncSession, cliente_cnpj_factory):
    repo = ClienteRepository(session)
    service = ClientService(repo)

    client = cliente_cnpj_factory.build()

    repo.session.add(client)
    await repo.session.commit()

    return_client = await service.get_by_id(client.id)

    assert return_client.id == client.id
    assert return_client.name == client.name


@pytest.mark.asyncio
async def test_deve_listar_com_filtro(session: AsyncSession, cliente_cnpj_factory):
    repo = ClienteRepository(session)
    service = ClientService(repo)

    client = cliente_cnpj_factory.build()

    repo.session.add(client)
    await repo.session.commit()

    filtro = FilterClienteResponse(name=client.name)
    return_dict = await service.get_by_filter(filtro)

    assert return_dict['costumers'][0].name == client.name
