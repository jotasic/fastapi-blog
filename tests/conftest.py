import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import query
from app.config import settings
from app.database import get_session
from app.main import app
from app.models import BaseModel, User
from app.schemas import UserCreate
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
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def default_user_token_header(client: TestClient) -> dict[str, str]:
    return get_user_token(client=client, email=DEFAULT_USER_EMAIL, password=DEFAULT_USER_PASSWORD)


@pytest.fixture(scope="function")
def random_user_data(session: Session) -> tuple[User, str]:
    """
    테스트용 다른 사용자를 생성하고 (User 객체, 비밀번호) 튜플을 반환합니다.
    """
    email = random_email()
    password = random_password()  # 패턴을 만족하는 랜덤 비밀번호 생성
    user_in = UserCreate(email=email, nickname=random_nickname(), password=password)
    user = query.create_user(session=session, user_in=user_in)
    return user, password


@pytest.fixture(scope="function")
def random_user_token_header(client: TestClient, random_user_data) -> dict[str, str]:
    """
    다른 사용자의 인증 토큰 헤더를 생성합니다.
    """
    user, password = random_user_data
    return get_user_token(client=client, email=user.email, password=password)
