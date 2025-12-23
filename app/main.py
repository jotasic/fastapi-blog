from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import main
from app.config import settings
from app.core.logging_config import setup_logging
from app.utils import get_custom_swagger_ui_html


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title="Blog App",
    description="Blog App의 api 입니다",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


app.include_router(
    main.api_v1_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/docs", include_in_schema=False)
async def get_docs():
    return get_custom_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Blog App API",
        swagger_ui_parameters={
            "layout": "StandaloneLayout",
        },
    )
