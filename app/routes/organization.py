from fastapi import APIRouter, HTTPException, Depends, status
from app.models import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.services.org_service import OrganizationService
from app.utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer
import pymongo

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

async def get_admin_payload(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

@router.post("/org/create", response_model=OrganizationResponse)
async def create_organization(org: OrganizationCreate):
    service = OrganizationService()
    return await service.create_organization(org)

@router.get("/org/get")
async def get_organization(organization_name: str):
    service = OrganizationService()
    return await service.get_organization(organization_name)

@router.put("/org/update")
async def update_organization(org_update: OrganizationUpdate, current_payload: dict = Depends(get_admin_payload)):
    service = OrganizationService()
    return await service.update_organization(
        org_update, 
        current_admin_email=current_payload["sub"],
        current_org_name=current_payload["org"]
    )

@router.delete("/org/delete")
async def delete_organization(organization_name: str, current_payload: dict = Depends(get_admin_payload)):
    service = OrganizationService()
    return await service.delete_organization(
        organization_name, 
        current_org_name=current_payload["org"],
        current_admin_email=current_payload["sub"]
    )
