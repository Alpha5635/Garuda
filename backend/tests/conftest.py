import os
import sys
import uuid
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure app path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.workers.celery_app import celery_app
from app.workers import tasks
from app.models.base import Base
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.dependencies import get_db
from app.main import app

# Configure Celery eager mode for tests
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True

# Test SQLite Database
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_app.db"))
TEST_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE}"
TEST_SYNC_DATABASE_URL = f"sqlite:///{DB_FILE}"

from sqlalchemy.pool import NullPool

test_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    poolclass=NullPool,
)
test_sync_engine = create_engine(
    TEST_SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)
tasks.sync_session_factory = sessionmaker(bind=test_sync_engine, autoflush=False, autocommit=False)


import pytest_asyncio

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    Base.metadata.create_all(bind=test_sync_engine)
    yield
    Base.metadata.drop_all(bind=test_sync_engine)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user():
    async with TestingSessionLocal() as session:
        pw_hash = AuthService.hash_password("TestPassword@123")
        user = User(
            id=uuid.uuid4(),
            email=f"testofficer_{uuid.uuid4().hex[:6]}@lm.gov.in",
            password_hash=pw_hash,
            name="Test Officer",
            role=UserRole.OFFICER.value
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
def auth_headers(test_user):
    token = AuthService.create_access_token(
        data={"sub": str(test_user.id), "role": test_user.role, "email": test_user.email}
    )
    return {"Authorization": f"Bearer {token}"}
