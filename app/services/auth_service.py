from app.database import get_master_db
from app.utils import verify_password, create_access_token
from app.models import AdminLogin
from fastapi import HTTPException, status
from datetime import timedelta

class AuthService:
    def __init__(self):
        self.db = get_master_db()

    async def login_admin(self, login_data: AdminLogin):
        # Check if admin exists
        admin = await self.db.admins.find_one({"email": login_data.email})
        if not admin or not verify_password(login_data.password, admin["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": admin["email"], "org": admin["organization_name"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "organization_id": admin["organization_name"],
            "admin_email": admin["email"]
        }
