import logging
import os
import sys

# 프로젝트 루트 경로를 sys.path에 추가하여 app 모듈을 찾을 수 있게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    confirm = input("recreate tables? (y/n): ")
    if confirm.lower() != "y":
        logger.info("Cancelled.")
        return

    logger.info("Start")

    with engine.begin() as conn:
        logger.info("Drop tables")
        BaseModel.metadata.drop_all(conn)
        logger.info("Create tables")
        BaseModel.metadata.create_all(conn)

    logger.info("Done.")


if __name__ == "__main__":
    main()
