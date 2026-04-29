from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.core.database import get_session
from apisisbro.schemas.schema import (
    UserCreate,
    UserPublic,
)
from apisisbro.services.auth_service import (
    create_by_email,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/create', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserCreate, db: Session):
    try:
        return await create_by_email(user, db)
    except ValueError as err:
        status = HTTPStatus.BAD_REQUEST
        if 'já cadastrado' in str(err) or 'já está em uso' in str(err):
            status = HTTPStatus.CONFLICT
        raise HTTPException(
            status_code=status,
            detail=str(err),
        ) from err
