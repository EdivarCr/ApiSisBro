from http import HTTPStatus

import pytest


def _build_payload_pvd(pvd):
    return {
        'id_cliente': pvd.id_cliente,
        'name': pvd.name,
        'tipo_zona': pvd.tipo_zona.value,
        'endereco': pvd.endereco,
        'telefone': pvd.telefone,
        'instagram': pvd.instagram,
        'google_maps_url': pvd.google_maps_url,
        'latitude': pvd.latitude,
        'longitude': pvd.longitude,
    }


@pytest.mark.asyncio
async def test_route_deve_criar_pvd_com_sucesso(
    client, user, logar_usuario, cliente_cnpj_factory, pvd_cliente, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()

    pvd = pvd_cliente.build(id_cliente=cliente.id)
    payload = _build_payload_pvd(pvd)

    response = client.post('/pvd/', json=payload)

    assert response.status_code == HTTPStatus.CREATED
    json_data = response.json()
    assert json_data['name'] == payload['name']
    assert json_data['id_cliente'] == cliente.id
    assert 'id' in json_data


@pytest.mark.asyncio
async def test_route_deve_listar_pvd_com_sucesso(
    client, user, logar_usuario, cliente_cnpj_factory, pvd_cliente, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()

    pvd = pvd_cliente.build(id_cliente=cliente.id)
    session.add(pvd)
    await session.commit()

    response = client.get('/pvd/')

    assert response.status_code == HTTPStatus.OK
    json_data = response.json()

    assert 'pvds' in json_data
    assert 'offset' in json_data
    assert 'limit' in json_data
    assert isinstance(json_data['pvds'], list)
    assert len(json_data['pvds']) > 0
    assert json_data['pvds'][0]['name'] == pvd.name


@pytest.mark.asyncio
async def test_route_deve_listar_pvd_por_id_com_sucesso(
    client, user, logar_usuario, cliente_cnpj_factory, pvd_cliente, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()

    pvd = pvd_cliente.build(id_cliente=cliente.id)
    session.add(pvd)
    await session.commit()

    response = client.get(f'/pvd/{pvd.id}')

    assert response.status_code == HTTPStatus.OK
    json_data = response.json()

    assert json_data['id'] == pvd.id
    assert json_data['name'] == pvd.name
    assert json_data['id_cliente'] == cliente.id


@pytest.mark.asyncio
async def test_route_deve_listar_pvd_por_filtro_com_sucesso(
    client, user, logar_usuario, cliente_cnpj_factory, pvd_cliente, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()

    pvd = pvd_cliente.build(id_cliente=cliente.id, name='PVD Filtro')
    session.add(pvd)
    await session.commit()

    payload = {
        'name': 'PVD Filtro',
        'limit': 10,
        'offset': 0,
    }

    response = client.get('/pvd/pesquisa', params=payload)
    print('\n[ERRO 422 DETALHADO]:', response.json())
    assert response.status_code == HTTPStatus.OK
    json_data = response.json()

    assert 'pvds' in json_data
    assert len(json_data['pvds']) > 0
    assert json_data['pvds'][0]['name'] == pvd.name


@pytest.mark.asyncio
async def test_route_deve_atualizar_pvd_com_sucesso(
    client, user, logar_usuario, cliente_cnpj_factory, pvd_cliente, session
):
    logar_usuario(user)

    cliente = cliente_cnpj_factory.build()
    session.add(cliente)
    await session.commit()

    pvd = pvd_cliente.build(id_cliente=cliente.id)
    session.add(pvd)
    await session.commit()

    payload = {
        'name': 'PVD Atualizado',
        'endereco': 'Rua Nova, 999',
        'tipo_zona': pvd.tipo_zona.value,
    }

    response = client.patch(f'/pvd/{pvd.id}', json=payload)

    assert response.status_code == HTTPStatus.OK
    json_data = response.json()

    assert json_data['id'] == pvd.id
    assert json_data['name'] == payload['name']
    assert json_data['endereco'] == payload['endereco']
