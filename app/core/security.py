import copy
from datetime import UTC, datetime, timedelta

import jwt
import pwdlib.exceptions
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import settings

password_hash = PasswordHash((BcryptHasher(),))


def create_password_hash(password: str):
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str):
    try:
        return password_hash.verify(password, hashed_password)
    except pwdlib.exceptions.UnknownHashError:
        # TODO: LOGGING 추가
        return False


def create_access_token(sub: str, data: dict | None = None):
    data = copy.deepcopy(data) if data is not None else []

    current = datetime.now(UTC)

    data["iat"] = current
    data["sub"] = sub
    data["exp"] = current + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(data, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_access_token(token: str):
    try:
        data = jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return data
    except jwt.exceptions.PyJWTError:
        return None
