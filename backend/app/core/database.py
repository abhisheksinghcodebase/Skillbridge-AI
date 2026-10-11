"""
SkillBridge AI — MongoDB Database Connection & Manager using Motor.
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

# Global client and database instances
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create the Motor client singleton."""
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client


def get_database() -> AsyncIOMotorDatabase:
    """Get or create the Motor database singleton."""
    global db
    if db is None:
        c = get_mongo_client()
        db = c[settings.MONGODB_DB_NAME]
    return db


async def get_db() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency that returns the active MongoDB database instance.
    """
    return get_database()


async def connect_to_mongo():
    """
    Connect to MongoDB and ensure indexes for optimal query performance.
    """
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    # Create indexes for collections
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        await db.resumes.create_index("id", unique=True)
        await db.resumes.create_index("user_id")
        await db.resumes.create_index([("user_id", 1), ("created_at", -1)])
        await db.chat_messages.create_index("id", unique=True)
        await db.chat_messages.create_index("user_id")
        await db.chat_messages.create_index([("user_id", 1), ("session_id", 1), ("created_at", -1)])
        await db.roadmaps.create_index("id", unique=True)
        await db.roadmaps.create_index("user_id")
        await db.github_analyses.create_index("id", unique=True)
        await db.github_analyses.create_index("user_id")
        await db.learning_progress.create_index("id", unique=True)
        await db.learning_progress.create_index("user_id")
        await db.interview_sessions.create_index("id", unique=True)
        await db.interview_sessions.create_index("user_id")
    except Exception as e:
        print(f"Warning: Index creation error (may occur if MongoDB is offline or in mock mode): {e}")


async def close_mongo_connection():
    """
    Close MongoDB client connections gracefully.
    """
    global client, db
    if client is not None:
        client.close()
        client = None
        db = None
