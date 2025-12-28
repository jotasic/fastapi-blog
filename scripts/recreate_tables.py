import logging
import os
import sys

import anyio

# 프로젝트 루트 경로를 sys.path에 추가하여 app 모듈을 찾을 수 있게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_engine
from app.core.logging_config import setup_logging
from app.models.base import BaseModel

logger = logging.getLogger()


async def main():
    confirm = input("recreate tables? (y/n): ")
    if confirm.lower() != "y":
        logger.info("Cancelled.")

    logger.info("Start")

    async with async_engine.begin() as conn:
        logger.info("Drop tables")
        await conn.run_sync(BaseModel.metadata.drop_all)
        logger.info("Create tables")
        await conn.run_sync(BaseModel.metadata.create_all)

    logger.info("Done.")


if __name__ == "__main__":
    setup_logging()
    anyio.run(main)
