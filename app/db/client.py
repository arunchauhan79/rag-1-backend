import asyncio
from pymongo import AsyncMongoClient
from core import settings,DatabaseConnectionException
from pymongo.errors import ConnectionFailure, OperationFailure

# --- Configuration ---
# Replace with your MongoDB connection string

DATABASE_NAME = "ai-chatbot-with-python" # Renamd to differentiate from collection name

# --- Global Client Variable ---
_client = None

# --- Database Connection Function ---
def get_database():
    """
    Establishes and returns a MongoDB database object.
    Uses a global client to ensure only one connection is made.
    """
    global _client
    if _client is None:
        try:
            _client = AsyncMongoClient(settings.mongodb_uri)
            _client.admin.command('ping')
           
            print("MongoDB connection successful!")
            return _client[DATABASE_NAME]
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            _client = None # Reset client if connection fails
            raise DatabaseConnectionException(f"MongoDB connection failed")
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            _client = None
            raise DatabaseConnectionException(f"An unexpected error occurred during connection")
    else:
        # If client already exists, just return the database
        print("Database object",_client[DATABASE_NAME])
        return _client[DATABASE_NAME]

async def close_db_connection():
    """Closes the MongoDB client connection if it exists."""
    global _client
    if _client:
        await  _client.close()
        _client = None # Reset client after closing
        print("MongoDB connection closed.")

# You can add a main guard here for testing this file independently
if __name__ == "__main__":
    dbName = asyncio.run(get_database())
    if dbName:
        print(f"Successfully connected to database: {dbName.name}")
        # Example: List existing collection names
    close_db_connection()