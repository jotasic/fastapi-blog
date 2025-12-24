# https://www.structlog.org/en/stable/standard-library.html
import json
import logging.config
from typing import Any

import structlog
from asgi_correlation_id import correlation_id

from app.core.config import settings


def extract_from_record(_, __, event_dict):
    """
    Standard Logging의 LogRecord 객체에서 파일/라인 정보를 추출하여
    structlog event_dict로 복사한다.
    """

    # key값을 그냥 문자로 써도 되지만 더 영확하게 하기 위해서 다음과 같이 structlog의 enum으로 정의함.
    record = event_dict.get("_record")
    if record:
        event_dict[structlog.processors.CallsiteParameter.FILENAME.value] = record.filename
        event_dict[structlog.processors.CallsiteParameter.FUNC_NAME.value] = record.funcName
        event_dict[structlog.processors.CallsiteParameter.LINENO.value] = record.lineno
    return event_dict


def add_correlation(logger: logging.Logger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    if request_id := correlation_id.get():
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging() -> None:
    message_key = "message"  # 로그 메세지의 key 값 (기본: event)

    # 1. 공통 타임스탬프 설정 (ISO 포맷)
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    if settings.ENVIRONMENT == "local":
        root_level = logging.DEBUG
        sql_level = logging.INFO
        uvicorn_level = logging.INFO
        format_type = "console"

        foreign_pre_chain = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.ExtraAdder(),
            timestamper,
        ]

        structlog_processors = [
            # 비동기 환경(FastAPI)에서 ContextVars(Request ID 등) 병합
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

    else:
        root_level = logging.INFO
        sql_level = logging.WARNING
        uvicorn_level = logging.INFO
        format_type = "json"

        foreign_pre_chain = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.ExtraAdder(),
            timestamper,
        ]

        structlog_processors = [
            # 비동기 환경(FastAPI)에서 ContextVars(Request ID 등) 병합
            structlog.contextvars.merge_contextvars,
            # 호출 위치 정보 추가 (스택 오염 전 실행)
            # 인자 없이 사용 시 기본값(filename, func_name, lineno 그외) 자동 적용
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

    # 2. 외부 라이브러리(Standard Logging)가 structlog 포맷터로 들어오기 전 거치는 전처리
    # structlog.configure(processors=[]) 와 최대한 비슷하게 한다

    logging.config.dictConfig(
        {
            "version": 1,
            # 설정파일에 없는 로거를 비활성화 시킬지 여부
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        add_correlation,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.EventRenamer(message_key),
                        structlog.dev.ConsoleRenderer(colors=True, event_key=message_key),
                    ],
                    "foreign_pre_chain": foreign_pre_chain,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        add_correlation,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.dict_tracebacks,
                        structlog.processors.EventRenamer(message_key),
                        structlog.processors.JSONRenderer(serializer=json.dumps, ensure_ascii=False),
                    ],
                    "foreign_pre_chain": foreign_pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": format_type,
                },
            },
            "loggers": {
                "": {"handlers": ["default"], "level": root_level, "propagate": True},
                "uvicorn": {"handlers": ["default"], "level": uvicorn_level, "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": uvicorn_level, "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "level": uvicorn_level, "propagate": False},
                "fastapi": {"handlers": ["default"], "level": root_level, "propagate": False},
                "sqlalchemy.engine": {"handlers": ["default"], "level": sql_level, "propagate": False},
            },
        }
    )

    structlog.configure(
        processors=structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
