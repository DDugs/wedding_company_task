from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

# Default to localhost
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_DETAILS)

# Master Database
master_db = client.master_db
organization_collection = master_db.get_collection("organizations")

def get_master_db():
    return master_db

def get_org_db(org_name: str):
    collection_name = f"org_{org_name}"
    return master_db.get_collection(collection_name)

async def close_mongo_connection():
    client.close()
