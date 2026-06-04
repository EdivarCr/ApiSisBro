from datetime import datetime

import factory
import jwt
import pytest
import pytest_asyncio
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from apisisbro.app import app
from apisisbro.core.database import get_session
from apisisbro.core.settings import settings
from apisisbro.models.models import User, table_registry

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda n: f'{n.username}@test.com')
    password = factory.LazyAttribute(lambda n: f'{n.username}')

    def generate_token(self):
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1),
            'iat': datetime.datetime.now(tz=datetime.UTC),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        engine_return = create_async_engine(postgres.get_connection_url())
        yield engine_return


@pytest_asyncio.fixture
async def session(engine):

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_test():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_test
        yield client


@pytest_asyncio.fixture
async def user(session):
    password = 'pimenta'
    user = UserFactory(password=settings.get_password_hash(password))

    session.add(user)
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'testtest'
    user = UserFactory(password=settings.get_password_hash(password))

    session.add(user)
    await session.refresh(user)

    user.clean_password = password

    return user
