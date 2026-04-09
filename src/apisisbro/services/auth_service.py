from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import User
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
    auth_response = client.auth.exchange_code_for_session({'auth_code': code})

    session = auth_response.session
    user_info = auth_response.user

    # 2. Extrai dados do Google
    email = user_info.email
    name = user_info.user_metadata.get('full_name', '')
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
