import asyncio
from pymongo import AsyncMongoClient
from core import settings,DatabaseConnectionException
from pymongo.errors import ConnectionFailure, OperationFailure


# --- Global Variables ---
_client = None
_database = None

DATABASE_NAME = settings.DATABASE_NAME

# --- Database Initialization Function ---
def initialize_database():
    """
    Initializes the MongoDB client and database objects.
    Should be called once during application startup.
    """
    global _client, _database
    if _client is None:
        try:
            _client = AsyncMongoClient(settings.mongodb_uri)
            _database = _client[DATABASE_NAME]
            print("MongoDB connection successful!")
            return _database
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            _client = None
            _database = None
            raise DatabaseConnectionException(f"MongoDB connection failed")
        except Exception as e:
            _client = None
            _database = None
            raise DatabaseConnectionException(f"An unexpected error occurred during connection")
    return _database

# --- Database Connection Function ---
def get_database():
    """
    Returns the global database object.
    If not initialized, initializes it first.
    """
    global _database
    if _database is None:
        return initialize_database()
    return _database

async def close_db_connection():
    """Closes the MongoDB client connection if it exists."""
    global _client, _database
    if _client:
        await _client.close()
        _client = None # Reset client after closing
        _database = None # Reset database after closing
        print("MongoDB connection closed.")

# You can add a main guard here for testing this file independently
if __name__ == "__main__":
    async def test_connection():
        try:
            db = initialize_database()
            if db:
                print(f"Successfully connected to database: {db.name}")
                # Test a simple command
                result = await db.command("ping")
                print(f"Ping result: {result}")
        except Exception as e:
            print(f"Connection test failed: {e}")
        finally:
            await close_db_connection()
    
    asyncio.run(test_connection())