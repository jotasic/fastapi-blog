import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.main import app
from app.models import BaseModel
from tests.utils import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD, get_user_token, init_test_data


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.DATABASE_TEST_URI)
    yield engine
    engine.dispose()


# 2. [Session Scope] 테이블 생성/삭제 (테스트 전체에 1번만 실행)
@pytest.fixture(scope="session", autouse=True)
def setup_schema(db_engine):
    BaseModel.metadata.create_all(bind=db_engine)
    with Session(db_engine) as session:
        init_test_data(session)

    yield

    BaseModel.metadata.drop_all(bind=db_engine)
    db_engine.dispose()


@pytest.fixture(scope="function")
def session(db_engine):
    # 실제 DB 연결을 가져옴
    connection = db_engine.connect()
    # 외곽 트랜잭션 시작
    transaction = connection.begin()
    # 중첩 트랜잭션(Savepoint)을 사용하여 내부 commit을 무력화
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

    # 테스트 끝나면 오버라이드 해제
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def default_user_token_header(client: TestClient) -> dict[str, str]:
    return get_user_token(client=client, email=DEFAULT_USER_EMAIL, password=DEFAULT_USER_PASSWORD)
