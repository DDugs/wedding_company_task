import asyncio
import httpx
import os
import logging
from fastapi import FastAPI
from app.routes import auth, organization
from app.database import close_mongo_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Organization Management Service")

app.include_router(auth.router)
app.include_router(organization.router)

async def start_self_ping():
    """
    Periodically pings the application to keep it awake on Render.
    """
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        logger.warning("RENDER_EXTERNAL_URL not set. Self-ping disabled.")
        return

    # Ensure URL ends with /health
    health_url = f"{url}/health"
    logger.info(f"Starting self-ping to {health_url}")

    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(health_url)
                if response.status_code == 200:
                    logger.info("Self-ping successful: Application is awake.")
                else:
                    logger.warning(f"Self-ping returned status: {response.status_code}")
        except Exception as e:
            logger.error(f"Self-ping failed: {e}")
        
        # Wait for 14 minutes (Render sleeps after 15 mins of inactivity)
        await asyncio.sleep(840)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_self_ping())

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Welcome to Organization Management Service"}

