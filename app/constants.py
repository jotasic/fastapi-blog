from dataclasses import dataclass
from enum import StrEnum


class APITagName(StrEnum):
    V1 = "v1"
    USER = "user"
    AUTH = "auth"
    POST = "post"


@dataclass(frozen=True)
class APITagMetadata:
    VERSION = [
        {"name": APITagName.V1, "description": "v1"},
    ]

    APP = [
        {"name": APITagName.AUTH, "description": "auth api"},
        {"name": APITagName.USER, "description": "user api"},
        {"name": APITagName.POST, "description": "post api"},
    ]

    ALL = VERSION + APP


PASSWORD_PATTERN = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])[A-Za-z\d!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]{8,16}$"  # noqa: E501


class EmailVerificationAction(StrEnum):
    SIGNUP = "signup"
