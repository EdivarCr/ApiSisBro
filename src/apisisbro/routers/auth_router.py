from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.auth import get_curren_user
from apisisbro.core.database import get_session
from apisisbro.models.models import User
from apisisbro.schemas.schema import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
    UserLogin,
)
from apisisbro.services.auth_service import (
    exchange_code_and_get_or_create_user,
    generate_google_login_url,
    login_email,
    send_recovery_email,
    update_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_user = Annotated[User, Depends(get_curren_user)]


@router.get('/login')
def login():
    url = generate_google_login_url(redirect_to='http://localhost:8000/auth/callback')
    return RedirectResponse(url=url)


@router.get('/callback')
async def callback(code: str, db: Session):

    if not code:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='code not found')
    try:
        _, access_token = await exchange_code_and_get_or_create_user(code, db)
    except ValueError as err:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(err)
        ) from err

    response = RedirectResponse(url='/auth/me')
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,  # True em produção (HTTPS)
        samesite='lax',
        max_age=3600,
    )
    return response


@router.get('/logout')
async def logout():
    response = RedirectResponse(url='/')
    response.delete_cookie('access_token')
    return response


@router.get('/me')
async def me(user: Current_user):
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
    }


@router.post('/login-by-email', status_code=HTTPStatus.OK, response_model=Token)
async def login_by_email(user: UserLogin, db: Session, response: Response):
    try:
        token_data = await login_email(user, db)

        response.set_cookie(
            key='access_token',
            value=token_data['access_token'],
            httponly=True,
            secure=False,
            samesite='lax',
            max_age=3600,
        )
        return token_data
    except ValueError as err:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=str(err),
        ) from err


@router.post('/forgot-password', status_code=HTTPStatus.OK)
def recover_password(request: ForgotPasswordRequest):
    return send_recovery_email(request.email, request.redirect_url)


@router.post('/reset-password')
def reset_password(request: ResetPasswordRequest):
    return update_password(
        request.access_token, request.refresh_token, request.new_password)
