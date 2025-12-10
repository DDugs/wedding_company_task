from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Organization Schemas
class OrganizationCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrganizationUpdate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrganizationResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    
    class Config:
        from_attributes = True

# Admin Login Schemas
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    organization_id: Optional[str] = None
    admin_email: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None
