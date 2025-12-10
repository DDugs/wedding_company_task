from fastapi import APIRouter, HTTPException, status, Depends
from app.models import AdminLogin, Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/admin/login", response_model=Token)
async def login_for_access_token(bs: AdminLogin):
    auth_service = AuthService()
    return await auth_service.login_admin(bs)
