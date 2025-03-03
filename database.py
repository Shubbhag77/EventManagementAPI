from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


client = AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.DATABASE_NAME]


events_collection = database.events
attendees_collection = database.attendees

async def connect_to_mongodb():
    try:
        await client.admin.command('ping')
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongodb_connection():
    client.close()
    print("MongoDB connection closed.")