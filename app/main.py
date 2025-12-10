from fastapi import FastAPI
from app.routes import auth, organization
from app.database import close_mongo_connection

app = FastAPI(title="Organization Management Service")

app.include_router(auth.router)
app.include_router(organization.router)

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to Organization Management Service"}
