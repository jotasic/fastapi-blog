from dataclasses import dataclass
from enum import StrEnum


class APITagName(StrEnum):
    V1 = "v1"
    USER = "user"
    AUTH = "auth"


@dataclass(frozen=True)
class APITagMetadata:
    VERSION = [
        {"name": APITagName.V1, "description": "v1"},
    ]

    APP = [
        {"name": APITagName.USER, "description": "user api"},
        {"name": APITagName.USER, "description": "auth api"},
    ]

    ALL = VERSION + APP
