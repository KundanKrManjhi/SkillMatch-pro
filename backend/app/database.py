
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings

client = AsyncIOMotorClient(
    settings.mongodb_url,
    serverSelectionTimeoutMS=4000
)

db = client[settings.database_name]