from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest


@patch('apisisbro.services.auth_service.supabase')
@pytest.mark.asyncio
async def test_token(mock_supabase, client):
    mock_session_response = MagicMock()
    mock_session_response.session.access_token = 'token12312310401adknaoda.adiadn'
    mock_session_response.session.token_type = 'bearer'
    mock_session_response.user.id = '1'

    mock_supabase.auth.sign_in_with_password.return_value = mock_session_response

    # 2. DISPARA A REQUISIÇÃO PARA A SUA ROTA
    # Aqui você está testando o comportamento real da sua API
    response = client.post("/auth/login-by-email", json={
        "email": "usuario@teste.com",
        "password": "senhasegura.123"
    })

    # 3. VALIDA AS RESPOSTAS DA SUA ROTA
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "access_token": "token12312310401adknaoda.adiadn",
        "token_type": 'bearer'
            }

    # Garante que a sua rota realmente tentou chamar o Supabase com os dados certos
    mock_supabase.auth.sign_in_with_password.assert_called_once_with({
        "email": "usuario@teste.com",
        "password": "senhasegura.123"
    })


@patch('apisisbro.services.auth_service.supabase')
@pytest.mark.asyncio
async def test_token_unauthorized(mock_supabase, client):
    mock_session_response = MagicMock()
    mock_session_response.session.access_token = 'adiadn'
    mock_session_response.session.token_type = 'bearer'
    mock_session_response.user.id = '1'

    mock_supabase.auth.sign_in_with_password.return_value = mock_session_response

    response = client.post('/auth/login-by-email', json = {
        "email": "errorname",
        "password": "senhasegura.123"
    })

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'err': 'value error'
    }

    mock_supabase.auth.sign_in_with_password.assert_called_once_with({
        "email": "usuario@teste.com",
        "password": "senhasegura.123"
    })
