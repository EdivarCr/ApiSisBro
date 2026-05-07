from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from supabase_auth.errors import AuthError

from apisisbro.models.models import User
from apisisbro.schemas.schema import ForgotPasswordRequest, UserCreate, UserLogin
from apisisbro.services.supabase_client import supabase


def generate_google_login_url(redirect_to: str) -> str:
    client = supabase
    response = client.auth.sign_in_with_oauth({
        'provider': 'google',
        'options': {'redirect_to': redirect_to},
    })
    return response.url


async def exchange_code_and_get_or_create_user(
    code: str, db: AsyncSession
) -> tuple[User, str]:
    """
    Recebe o code do OAuth, troca por sessão no Supabase,
    e cria ou busca o usuário no NOSSO banco.
    Retorna (user, access_token).
    """
    # 1. Troca o code por sessão no Supabase
    client = supabase
    try:
        auth_response = client.auth.exchange_code_for_session({'auth_code': code})
    except AuthError as err:
        raise ValueError('Código OAuth inválido ou expirado.') from err

    session = auth_response.session
    user_info = auth_response.user
    if not session or not user_info or not user_info.email or not session.access_token:
        raise ValueError('Código OAuth inválido ou expirado.')

    # 2. Extrai dados do Google
    email = user_info.email
    user_metadata = user_info.user_metadata or {}
    name = user_metadata.get('full_name') or email
    supabase_id = user_info.id

    # 3. Busca no nosso banco
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # 4. Se não existe, cria
    if not user:
        user = User(email=email, username=name, supabase_id=supabase_id, password='')
        db.add(user)
        await db.flush()  # gera o ID sem commitar (o commit é do get_session)

    return user, session.access_token


async def login_email(user: UserLogin, _db: AsyncSession) -> dict[str, str]:
    try:
        res = supabase.auth.sign_in_with_password({
            'email': str(user.email),
            'password': user.password,
        })
        if not res.session or not res.session.access_token:
            raise ValueError('Credenciais inválidas')
        return {
            'access_token': res.session.access_token,
            'token_type': 'bearer',
        }
    except AuthError as err:
        raise ValueError('Credenciais inválidas') from err


async def create_by_email(user: UserCreate, db: AsyncSession) -> User:
    existing_email = await db.scalar(select(User).where(User.email == str(user.email)))
    if existing_email:
        raise ValueError('E-mail já cadastrado')

    existing_username = await db.scalar(select(User).where(User.username == user.name))
    if existing_username:
        raise ValueError('Nome de usuário já está em uso')

    try:
        res = supabase.auth.sign_up({
            'email': str(user.email),
            'password': user.password,
        })
        if not res.user or not res.user.id:
            raise ValueError('Falha ao criar usuário no provedor de autenticação error')
    except AuthError as err:
        raise ValueError(f'Falha no Supabase Auth: {err}') from err

    db_user = User(
        username=user.name,
        email=str(user.email),
        password='',
        supabase_id=res.user.id,
    )
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user


def send_recovery_email(
       email: ForgotPasswordRequest, redirect_url: ForgotPasswordRequest):
    try:
        supabase.auth.reset_password_email(
            str(email),
            options={"redirect_t": redirect_url}
            )
        return {'message': 'Email de recuperação enviado com sucesso'}
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f'Erro ao enviar email: {str(e)}'
        ) from e


def update_password(access_token: str, refresh_token: str, new_password: str):
    try:
        supabase.auth.set_session(access_token, refresh_token)

        supabase.auth.update_user({'password': new_password})

        supabase.auth.sign_out()

        return {'message': 'Sua senha foi atualizada com sucesso'}
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Erro ao atualizar senha: {str(e)}',
        ) from e
