import pytest
import redis.asyncio as redis_async
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import crud
from app.core.config import get_setting
from app.core.database import get_session
from app.core.redis_client import get_async_redis
from app.main import app
from app.models.models import BaseModel, User
from app.schemas.user import UserCreate
from tests.utils import (
    DEFAULT_USER_EMAIL,
    DEFAULT_USER_PASSWORD,
    get_user_token,
    init_test_data,
    random_email,
    random_nickname,
    random_password,
)

settings = get_setting()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(settings.DATABASE_URI)
    yield engine
    await engine.dispose()


# 2. [Session Scope] 테이블 생성/삭제 (테스트 전체에 1번만 실행)
@pytest.fixture(scope="session", autouse=True)
async def setup_schema(db_engine):
    try:
        async with db_engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)

            async with AsyncSession(bind=conn, expire_on_commit=False) as session:
                await init_test_data(session)
    except OperationalError as e:
        pytest.exit(e, returncode=1)


@pytest.fixture(scope="session")
async def async_redis_pool():
    pool = redis_async.ConnectionPool.from_url(settings.CACHE_URI, decode_responses=True)
    initial_client = redis_async.Redis(connection_pool=pool)
    await initial_client.flushdb()
    await initial_client.aclose()

    yield pool
    await pool.disconnect()


# database
@pytest.fixture(scope="function")
async def session(db_engine):
    async with db_engine.connect() as connection:
        transaction = await connection.begin()

        # 3. 세션 생성 (Nested Transaction을 위한 설정)
        # join_transaction_mode="create_savepoint": 세션이 커밋하더라도 실제로는 savepoint만 생성됨
        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,  # 비동기 환경에서 필수 권장 옵션
        )

        yield session
        # 5. 정리 (순서 중요)
        await session.close()
        await transaction.rollback()


# redis
@pytest.fixture(scope="function")
async def async_redis_client(async_redis_pool):
    async with redis_async.Redis(connection_pool=async_redis_pool) as client:
        yield client
        await client.flushdb()


# client - api 테스 시 요청 시 사용
# 해당 fixture가 필요 시 api내에서 사용하는 session, async_redis_client의 dependency 맞춘다.
@pytest.fixture(scope="function")
async def client(session, async_redis_client):
    # 1. DB 세션 오버라이드
    async def override_get_session():
        yield session

    # 2. Redis 디펜던시 오버라이드
    async def override_get_redis():
        yield async_redis_client

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_async_redis] = override_get_redis

    # 3. TestClient 대신 httpx.AsyncClient 사용
    # ASGITransport를 통해 실제 서버를 띄우지 않고 앱과 직접 통신
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",  # 명시적으로 설정
    ) as ac:
        yield ac
    # 4. 종료 후 오버라이드 제거
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def default_user_token_header(client: AsyncClient) -> dict[str, str]:
    return await get_user_token(client=client, email=DEFAULT_USER_EMAIL, password=DEFAULT_USER_PASSWORD)


@pytest.fixture(scope="function")
async def random_user_data(session: AsyncSession) -> tuple[User, str]:
    """
    테스트용 다른 사용자를 생성하고 (User 객체, 비밀번호) 튜플을 반환합니다.
    """
    email = random_email()
    password = random_password()  # 패턴을 만족하는 랜덤 비밀번호 생성
    user_in = UserCreate(email=email, nickname=random_nickname(), password=password)
    user = await crud.create_user(session=session, user_in=user_in)
    return user, password


@pytest.fixture(scope="function")
async def random_user_token_header(client: AsyncClient, random_user_data) -> dict[str, str]:
    """
    다른 사용자의 인증 토큰 헤더를 생성합니다.
    """
    user, password = random_user_data
    return await get_user_token(client=client, email=user.email, password=password)
