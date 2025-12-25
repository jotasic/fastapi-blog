import pytest
import redis.asyncio as redis_async
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
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
    random_password,  # random_password 임포트
)


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.DATABASE_TEST_URI)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function")
async def async_redis_client():
    async_redis_client = redis_async.from_url(settings.CACHE_URI, decode_responses=True)

    yield async_redis_client

    await async_redis_client.aclose()


# 2. [Session Scope] 테이블 생성/삭제 (테스트 전체에 1번만 실행)
@pytest.fixture(scope="session", autouse=True)
def setup_schema(db_engine):
    BaseModel.metadata.drop_all(bind=db_engine)
    BaseModel.metadata.create_all(bind=db_engine)
    with Session(db_engine) as session:
        init_test_data(session)

    yield

    BaseModel.metadata.drop_all(bind=db_engine)
    db_engine.dispose()


@pytest.fixture(scope="function")
def session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
async def client(session, async_redis_client):  # 이제 둘 다 비동기 컨텍스트에서 작동
    # 1. DB 세션 오버라이드
    def override_get_session():
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
def default_user_token_header(client: AsyncClient) -> dict[str, str]:
    return get_user_token(client=client, email=DEFAULT_USER_EMAIL, password=DEFAULT_USER_PASSWORD)


@pytest.fixture(scope="function")
def random_user_data(session: Session) -> tuple[User, str]:
    """
    테스트용 다른 사용자를 생성하고 (User 객체, 비밀번호) 튜플을 반환합니다.
    """
    email = random_email()
    password = random_password()  # 패턴을 만족하는 랜덤 비밀번호 생성
    user_in = UserCreate(email=email, nickname=random_nickname(), password=password)
    user = crud.create_user(session=session, user_in=user_in)
    return user, password


@pytest.fixture(scope="function")
def random_user_token_header(client: AsyncClient, random_user_data) -> dict[str, str]:
    """
    다른 사용자의 인증 토큰 헤더를 생성합니다.
    """
    user, password = random_user_data
    return get_user_token(client=client, email=user.email, password=password)
