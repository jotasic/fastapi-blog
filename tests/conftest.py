from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.main import app
from app.models import BaseModel

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.DATABASE_TEST_URI)
    yield engine
    engine.dispose()


# 2. [Session Scope] 테이블 생성/삭제 (테스트 전체에 1번만 실행)
@pytest.fixture(scope="session", autouse=True)
def setup_schema(db_engine):
    BaseModel.metadata.create_all(bind=db_engine)
    yield
    BaseModel.metadata.drop_all(bind=db_engine)


# 추후 롤백이 필요시 https://github.com/fastapi/sqlmodel/discussions/940 참고
@pytest.fixture(scope="session")
def session(db_engine) -> Generator[Session]:
    with Session(db_engine) as session:
        yield session


@pytest.fixture(scope="module")
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    # 테스트 끝나면 오버라이드 해제
    app.dependency_overrides.clear()
