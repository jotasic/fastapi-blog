import logging

from app.database import engine
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
