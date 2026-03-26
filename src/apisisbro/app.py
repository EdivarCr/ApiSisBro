from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .core.database import get_session
from .models.models import User as UserModel
from .schemas.schema import User, UserPublic

app = FastAPI(title='ApiSisBro')

Session = Annotated[AsyncSession, Depends(get_session)]


@app.post('/')
def message():
    return {'message': 'helo word'}


@app.post('/user', response_model=UserPublic)
async def create_user(user: User, session: Session):
    db_user = await session.scalar(
        select(UserModel).where(
            (UserModel.username == user.name) | (UserModel.email == user.email)
        )
    )

    db_user = UserModel(
        username=user.name,
        email=user.email,
        password=user.password,  # Lembre-se de usar hash no futuro!
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user
