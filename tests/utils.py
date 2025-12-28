import random
import string
from typing import TYPE_CHECKING

from app import crud
from app.schemas import PostCreate, UserCreate

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Post, User


DEFAULT_USER_EMAIL = "example@test.com"
DEFAULT_USER_NICKNAME = "user"
DEFAULT_USER_PASSWORD = "Test1234!"


def random_lower_string(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"{random_lower_string(8)}@{random_lower_string(5)}.com"


def random_nickname() -> str:
    return f"user_{random_lower_string(5)}"


def random_password() -> str:
    """
    비밀번호 패턴(영문, 숫자, 특수문자 포함 8~16자)을 만족하는 랜덤 비밀번호 생성
    """
    length = random.randint(8, 16)

    chars = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]

    all_chars = string.ascii_letters + string.digits + string.punctuation
    chars += random.choices(all_chars, k=length - len(chars))

    random.shuffle(chars)

    return "".join(chars)


async def create_default_user(session: AsyncSession) -> User:
    user_in = UserCreate(
        email=DEFAULT_USER_EMAIL,
        nickname=DEFAULT_USER_NICKNAME,
        password=DEFAULT_USER_PASSWORD,
    )
    # handle 필드가 없으므로 query.create_user 호출만으로 충분합니다.
    user = await crud.create_user(session=session, user_in=user_in)
    return user


async def create_random_user(session: AsyncSession) -> User:
    email = random_email()
    nickname = random_nickname()
    password = random_password()

    user_in = UserCreate(
        email=email,
        nickname=nickname,
        password=password,
    )
    # handle 필드가 없으므로 query.create_user 호출만으로 충분합니다.
    user = await crud.create_user(session=session, user_in=user_in)
    return user


async def create_random_post(session: AsyncSession, user: User) -> Post:
    title = random_lower_string(15).capitalize()
    content = random_lower_string(100)
    # slug 필드가 없으므로 제거

    post_in = PostCreate(title=title, content=content, user_id=user.id)

    post = await crud.create_post(session=session, post_in=post_in)
    return post


async def init_test_data(session: AsyncSession):
    """
    테스트에 필요한 초기 데이터를 생성합니다.
    """
    default_user = await create_default_user(session)

    for _ in range(5):
        await create_random_post(session, default_user)


async def get_user_token(*, client: AsyncClient, email: str, password: str) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = await client.post("/v1/auth/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
