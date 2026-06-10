from datetime import UTC, datetime, timedelta, timezone

import factory
import jwt
import pytest
import pytest_asyncio
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from apisisbro.app import app
from apisisbro.core.auth import get_curren_user
from apisisbro.core.database import get_session
from apisisbro.core.settings import settings
from apisisbro.models.models import (
    Cliente,
    PontoDeVenda,
    TipoCliente,
    TipoZona,
    User,
    table_registry,
)

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User
        # A LINHA QUE CORRIGE O ERRO:
        # Impede o Factory Boy de tentar passar o 'id' no construtor da Dataclass
        exclude = ('id',)

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda n: f'{n.username}@test.com')
    password = factory.LazyAttribute(lambda n: f'{n.username}')
    supabase_id = factory.LazyAttribute(lambda _: fake.uuid4())

    @classmethod
    def generate_token(cls, user_obj: User):
        payload = {
            'user_id': user_obj.id,
            'username': user_obj.username,
            'exp': datetime.now(tz=UTC) + timedelta(days=1),
            'iat': datetime.now(tz=UTC),
        }
        return jwt.encode(
            payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.ALGORITHM
        )


class PvdFactory(factory.Factory):
    class Meta:
        model = PontoDeVenda

    id_cliente = None
    name = factory.Sequence(lambda n: f'Pvd{fake.company()[:20]}')
    tipo_zona = factory.Iterator([
        TipoZona.ZONA_NORTE,
        TipoZona.ZONA_SUL,
        TipoZona.ZONA_LESTE,
        TipoZona.ZONA_OESTE,
    ])
    endereco = factory.LazyAttribute(lambda _: fake.address())
    telefone = factory.LazyAttribute(lambda _: fake.phone_number()[:20])
    instagram = factory.LazyAttribute(lambda n: f'{n.name.lower().replace(" ", "")[:20]}')
    google_maps_url = factory.LazyAttribute(lambda _: fake.url())
    latitude = factory.LazyAttribute(lambda _: str(fake.latitude()))
    longitude = factory.LazyAttribute(lambda _: str(fake.longitude()))


class ClienteCnpjFactory(factory.Factory):
    class Meta:
        model = Cliente

    name = factory.Sequence(lambda n: f'Empório Alimentos {n}')
    tipo = TipoCliente.COMERCIO
    identificador = factory.Sequence(lambda n: f'123456780001{n:02d}')
    telefone = '85999998888'
    email = factory.Sequence(lambda n: f'contato{n}@emporio.com')
    endereco = 'Rua das Pimentas, 123 - Quixadá'


class ClienteCpfFactory(factory.Factory):
    class Meta:
        model = Cliente

    name = factory.Sequence(lambda n: f'Teste{n}')
    tipo = TipoCliente.PESSOA_FISICA
    identificador = factory.Sequence(lambda n: f'091279334{n:02d}')
    telefone = '85999998888'
    email = factory.Sequence(lambda n: f'contato{n}@gmail.com')
    endereco = 'Rua das Pimentas, 123 - Quixadá'


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
    """Gera o cliente apenas com o banco de dados isolado."""

    def get_session_test():
        return session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_test
        yield test_client
        app.dependency_overrides.clear()


@pytest.fixture
def logar_usuario():
    """Fixture utilitária para logar qualquer usuário dinamicamente."""

    def _logar(user_obj):
        # Injeta o usuário passado no override do FastAPI
        app.dependency_overrides[get_curren_user] = lambda: user_obj

    return _logar


@pytest_asyncio.fixture
async def user(session) -> User:
    password = 'pimenta'
    user = UserFactory(password=settings.get_password_hash(password))

    session.add(user)
    await session.flush()
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


@pytest.fixture
def cliente_cnpj_factory():
    return ClienteCnpjFactory


@pytest.fixture
def pvd_cliente():
    return PvdFactory
