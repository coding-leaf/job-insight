import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> bool:
        """Attempt to connect to MongoDB and ping the server."""
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=2000,
            )
            # Ping database to verify connection
            await self.client.admin.command("ping")
            self.db = self.client[settings.DATABASE_NAME]
            logger.info("Connected to MongoDB at %s", settings.MONGODB_URL)
            return True
        except (PyMongoError, OSError) as exc:
            logger.warning(
                "MongoDB connection at %s failed: %s. Repository fallback enabled.",
                settings.MONGODB_URL,
                exc,
            )
            self.db = None
            return False

    async def close(self) -> None:
        """Close connection to MongoDB."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Closed MongoDB connection.")

    def get_db(self) -> AsyncIOMotorDatabase | None:
        return self.db


db_manager = MongoDBManager()


def get_database() -> AsyncIOMotorDatabase | None:
    return db_manager.get_db()
