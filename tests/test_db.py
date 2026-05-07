import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apisisbro.models.models import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession):
    user = User(
        username='testuser',
        email='teste@teste.com',
        password='teste123',
        supabase_id=None,
    )

    session.add(user)
    await session.commit()

    user_query = await session.scalar(
        select(User).where(User.email == 'teste@teste.com')
    )

    assert user_query is not None
    assert user_query.id is not None
    assert user_query.username == 'testuser'
    assert user_query.email == 'teste@teste.com'
    assert user_query.password == 'teste123'
    assert user_query.supabase_id is None
    assert user_query.id == user.id
