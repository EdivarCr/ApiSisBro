from http import HTTPStatus

import pytest

from apisisbro.models.models import User
from tests.conftest import UserFactory


@pytest.mark.asyncio
async def test_route_deve_criar_cliente_com_sucesso(
    client, user: User, cliente_cnpj_factory, logar_usuario
):

    logar_usuario(user)

    # Dados do cliente
    cliente_mock = cliente_cnpj_factory.build()
    payload = {
        'name': cliente_mock.name,
        'tipo': cliente_mock.tipo.value,
        'identificador': cliente_mock.identificador,
        'telefone': cliente_mock.telefone,
        'email': cliente_mock.email,
        'endereco': cliente_mock.endereco,
    }

    # Requisição POST na API
    response = client.post('/clientes/', json=payload)

    # Asserts
    assert response.status_code == HTTPStatus.CREATED
    json_data = response.json()
    assert json_data['name'] == payload['name']
    assert 'id' in json_data


@pytest.mark.asyncio
async def test_route_deve_listar_clientes_com_sucesso(client, user, logar_usuario):
    logar_usuario(user)

    response = client.get('/clientes/')
    assert response.status_code == HTTPStatus.OK

    json_data = response.json()

    assert 'costumers' in json_data
    assert 'offset' in json_data
    assert 'limit' in json_data
    # Garante que 'costumers' dentro do objeto é uma lista real
    assert isinstance(json_data['costumers'], list)


@pytest.mark.asyncio
async def test_route_deve_listar_cliente_por_id_com_sucesso(
    client, user, logar_usuario, cliente_cnpj_factory, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()
    response = client.get(f'/clientes/{cliente.id}')

    assert response.status_code == HTTPStatus.OK

    json_data = response.json()

    assert json_data['id'] == cliente.id
    assert json_data['name'] == cliente.name
    assert json_data['identificador'] == cliente.identificador


@pytest.mark.asyncio
async def test_route_deve_listar_cliente_por_filtro(
    client, user, logar_usuario, cliente_cnpj_factory, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()

    query_params = {'name': cliente.name}
    response = client.get('/clientes/pesquisa', params=query_params)

    assert response.status_code == HTTPStatus.OK

    json_data = response.json()

    assert 'costumers' in json_data
    assert len(json_data['costumers']) > 0
    assert json_data['costumers'][0]['name'] == cliente.name
