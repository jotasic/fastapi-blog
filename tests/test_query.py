from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from nanoid import generate

from app import crud
from app.models import User
from app.schemas import PostCreate, PostFilterParams, UserCreate, VerificationCodeCreate, VerificationCodeRead
from tests.utils import DEFAULT_USER_EMAIL, random_email, random_lower_string

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@pytest.mark.anyio
async def test_create_user(session: Session):
    nickname = random_lower_string(User.nickname.type.length)
    email = random_email()
    password = "Test1234!"

    user_in = UserCreate(nickname=nickname, email=email, password=password)

    user_db = crud.create_user(session=session, user_in=user_in)

    assert user_in.nickname == user_db.nickname
    assert user_in.email == user_db.email


@pytest.mark.anyio
async def test_get_user_by_email(session: Session):
    user = crud.get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)
    assert user


@pytest.mark.anyio
async def test_get_post_list(session: Session):
    filter_params = PostFilterParams()
    posts = crud.get_post_list(session=session, params=filter_params)
    assert type(posts) is list


@pytest.mark.anyio
async def test_get_post_list_with_filter(session: Session):
    filter_params = PostFilterParams(end=datetime.now(UTC))
    posts = crud.get_post_list(session=session, params=filter_params)
    assert type(posts) is list
    assert len(posts) > 0

    filter_params = PostFilterParams(start=datetime.now(UTC))
    posts = crud.get_post_list(session=session, params=filter_params)
    assert type(posts) is list
    assert len(posts) == 0

    filter_params = PostFilterParams(order_direction="asc")
    posts = crud.get_post_list(session=session, params=filter_params)
    assert len(posts) > 0
    assert posts[0].created_at < posts[-1].created_at


@pytest.mark.anyio
async def test_get_post_by_short_id(session: Session):
    short_id = generate(size=12)
    post = crud.get_post_by_short_id(session=session, short_id=short_id)
    assert not post


@pytest.mark.anyio
async def test_create_post(session: Session):
    user = crud.get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)
    title = random_lower_string(20)
    content = random_lower_string(100)

    post_in = PostCreate(title=title, content=content, user_id=user.id)
    post_db = crud.create_post(session=session, post_in=post_in)
    assert post_in.title == post_db.title
    assert post_in.content == post_db.content
    assert post_db.user_id == user.id


@pytest.mark.anyio
async def test_create_read_verification_code(async_redis_client):
    email = random_email()
    code = generate(size=6)
    code_create = VerificationCodeCreate(email=email, action="signup", code=code)
    await crud.create_verification_code(async_redis_client, code_create)

    code_read = VerificationCodeRead(email=email, action="signup")
    code_out = await crud.get_verification_code(async_redis_client, code_read)

    assert code == code_out
