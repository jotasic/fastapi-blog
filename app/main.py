from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api import main
from app.config import settings
from app.constants import APITagMetadata, APITagName
from app.core.logging_config import setup_logging
from app.utils import get_custom_swagger_ui_html


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title="Blog App",
    description="Blog App의 api 입니다",
    openapi_url="/openapi_all.json",
    docs_url=None,
    redoc_url=None,
    openapi_tags=APITagMetadata.ALL,
    lifespan=lifespan,
)


app.include_router(main.api_v1_router, prefix=settings.API_V1_PREFIX, tags=[APITagName.V1])


@app.get("/docs", include_in_schema=False)
async def get_docs():
    return get_custom_swagger_ui_html(
        openapi_url="",
        title="Blog App API",
        swagger_ui_parameters={
            "urls": [
                {"name": "all", "url": "/openapi_all.json"},
                {"name": "v1", "url": "/openapi_v1.json"},
            ],
            "layout": "StandaloneLayout",
        },
    )


# 4. 버전별 openapi.json 엔드포인트 수동 개설
@app.get("/openapi_v1.json", include_in_schema=False)
async def get_openapi_v1():
    return get_openapi(title="v1 api", version="1.0.0", routes=main.api_v1_router.routes, tags=APITagMetadata.APP)
