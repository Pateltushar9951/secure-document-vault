"""
app/database.py
───────────────
MongoDB connection setup using mongoengine.
Initializes connection to MongoDB Atlas on app startup.
"""

from mongoengine import connect, disconnect
from app.config import get_settings

settings = get_settings()


def connect_db():
    """Connect to MongoDB Atlas."""
    try:
        connect(
            db=settings.MONGODB_DB_NAME,
            host=settings.MONGODB_URI,
        )
        print(f"✓ Connected to MongoDB Atlas: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise


def disconnect_db():
    """Disconnect from MongoDB."""
    disconnect()
    print("✓ Disconnected from MongoDB")

