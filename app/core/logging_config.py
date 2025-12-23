# https://www.structlog.org/en/stable/standard-library.html

import logging.config

import orjson
import structlog

from app.config import settings


def extract_from_record(_, __, event_dict):
    """
    Standard Logging의 LogRecord 객체에서 파일/라인 정보를 추출하여
    structlog event_dict로 복사한다.
    """

    # key값을 그냥 문자로 써도 되지만 더 영확하게 하기 위해서 다음과 같이 structlog의 enum으로 정의함.
    record = event_dict.get("_record")
    if record:
        event_dict[structlog.processors.CallsiteParameter.FILENAME] = record.filename
        event_dict[structlog.processors.CallsiteParameter.FUNC_NAME] = record.funcName
        event_dict[structlog.processors.CallsiteParameter.LINENO] = record.lineno
    return event_dict


def setup_logging() -> None:
    if settings.ENVIRONMENT == "local":
        root_level = "DEBUG"
        sql_level = "INFO"
        uvicorn_level = "INFO"
        format_type = "console"
    else:
        root_level = "INFO"
        sql_level = "WARNING"
        uvicorn_level = "INFO"
        format_type = "json"

    message_key = "message"  # 로그 메세지의 key 값 (기본: event)

    # 1. 공통 타임스탬프 설정 (ISO 포맷)
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    # 2. 외부 라이브러리(Standard Logging)가 structlog 포맷터로 들어오기 전 거치는 전처리
    # structlog.configure(processors=[]) 와 최대한 비슷하게 한다
    foreign_pre_chain = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        extract_from_record,  # LogRecord에서 위치 정보 추출
        timestamper,
    ]
    logging.config.dictConfig(
        {
            "version": 1,
            # 설정파일에 없는 로거를 비활성화 시킬지 여부
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        # 콘솔에서는 예외를 줄글로 보는게 편하므로 여기서 변환
                        structlog.processors.format_exc_info,
                        structlog.processors.EventRenamer(message_key),
                        structlog.dev.ConsoleRenderer(colors=True, event_key=message_key),
                    ],
                    "foreign_pre_chain": foreign_pre_chain,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.dict_tracebacks,
                        structlog.processors.EventRenamer(message_key),
                        structlog.processors.JSONRenderer(serializer=orjson.dumps),
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
                "uvicorn.error": {"level": uvicorn_level, "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "level": uvicorn_level, "propagate": False},
                "fastapi": {"handlers": ["default"], "level": root_level, "propagate": False},
                "sqlalchemy.engine": {"handlers": ["default"], "level": sql_level, "propagate": False},
            },
        }
    )

    structlog.configure(
        processors=[
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
            # 중요: format_exc_info를 여기서 제거함!
            # 이유는 Formatter 단계(console vs json)에서 각각 다르게 처리하기 위함.
            # 마지막에 반드시 필요 (std logging의 Formatter로 넘김)
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
