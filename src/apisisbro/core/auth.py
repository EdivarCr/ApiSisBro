from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from supabase_auth.errors import AuthError

from apisisbro.core.database import get_session
from apisisbro.models.models import User
from apisisbro.services.supabase_client import supabase

security = HTTPBearer(auto_error=False)
Session = Annotated[AsyncSession, Depends(get_session)]


async def get_curren_user(
    request: Request,
    db: Session,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:

    token = request.cookies.get('access_token')

    if not token:
        if credentials and credentials.scheme.lower() == 'bearer':
            token = credentials.credentials

    if not token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Não autenticado')

    try:
        response = supabase.auth.get_user(token)
    except AuthError as err:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Token inválido ou expirado'
        ) from err

    if not response or not response.user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='user not found')

    email = response.user.email
    if not email:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Token sem email de usuário'
        )

    user = await db.scalar(select(User).where(User.email == email))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado no sistema',
        )

    return user
