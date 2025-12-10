from app.database import get_master_db, get_org_db
from app.models import OrganizationCreate, OrganizationUpdate
from app.utils import get_password_hash
from fastapi import HTTPException, status
import pymongo

class OrganizationService:
    def __init__(self):
        self.master_db = get_master_db()

    async def create_organization(self, org: OrganizationCreate):
        # 1. Validate organization name does not exist
        if await self.master_db.organizations.find_one({"name": org.organization_name}):
            raise HTTPException(status_code=400, detail="Organization already exists")
        
        # 2. Validate email unique
        if await self.master_db.admins.find_one({"email": org.email}):
            raise HTTPException(status_code=400, detail="Admin email already registered")

        # 3. Create Admin User
        hashed_pwd = get_password_hash(org.password)
        admin_data = {
            "email": org.email,
            "hashed_password": hashed_pwd,
            "organization_name": org.organization_name
        }
        await self.master_db.admins.insert_one(admin_data)

        # 4. Create Organization Metadata
        org_collection_name = f"org_{org.organization_name}"
        org_data = {
            "name": org.organization_name,
            "collection_name": org_collection_name,
            "admin_email": org.email
        }
        await self.master_db.organizations.insert_one(org_data)

        # 5. Dynamically create collection
        # Note: We access get_org_db logic directly here or via the helper.
        # Ideally the service should handle the DB connection logic too, but reusing helper is fine.
        org_db_collection = get_org_db(org.organization_name)
        await org_db_collection.insert_one({"type": "init", "info": "Organization Created"})

        return {
            "organization_name": org.organization_name,
            "collection_name": org_collection_name,
            "admin_email": org.email
        }

    async def get_organization(self, organization_name: str):
        org = await self.master_db.organizations.find_one({"name": organization_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return {
            "organization_name": org["name"],
            "collection_name": org["collection_name"],
            "admin_email": org["admin_email"]
        }

    async def update_organization(self, org_update: OrganizationUpdate, current_admin_email: str, current_org_name: str):
        old_org_name = current_org_name
        new_org_name = org_update.organization_name
        
        # 1. Check if name change is requested and valid
        if old_org_name != new_org_name:
            if await self.master_db.organizations.find_one({"name": new_org_name}):
                raise HTTPException(status_code=400, detail="Organization name already taken")

            # Rename collection
            old_collection_name = f"org_{old_org_name}"
            new_collection_name = f"org_{new_org_name}"
            
            try:
                await self.master_db[old_collection_name].rename(new_collection_name)
            except pymongo.errors.OperationFailure:
                pass 
                
            # Update Master DB Org
            await self.master_db.organizations.update_one(
                {"name": old_org_name},
                {"$set": {"name": new_org_name, "collection_name": new_collection_name}}
            )
            
            # Update Admin User Org Reference
            await self.master_db.admins.update_one(
                {"email": current_admin_email},
                {"$set": {"organization_name": new_org_name}}
            )
        
        # 2. Update Admin Credentials if requested
        update_fields = {}
        if org_update.email != current_admin_email:
             if await self.master_db.admins.find_one({"email": org_update.email}):
                 raise HTTPException(status_code=400, detail="Email already taken")
             update_fields["email"] = org_update.email
        
        if org_update.password:
            update_fields["hashed_password"] = get_password_hash(org_update.password)
            
        if update_fields:
             await self.master_db.admins.update_one(
                {"email": current_admin_email},
                {"$set": update_fields}
            )
             if "email" in update_fields:
                target_org_name = new_org_name if old_org_name != new_org_name else old_org_name
                await self.master_db.organizations.update_one(
                    {"name": target_org_name},
                    {"$set": {"admin_email": update_fields["email"]}}
                )

        return {"status": "success", "message": "Organization updated"}

    async def delete_organization(self, organization_name: str, current_org_name: str, current_admin_email: str):
        if current_org_name != organization_name:
             raise HTTPException(status_code=403, detail="Not authorized to delete this organization")
             
        # Delete collection
        collection_name = f"org_{organization_name}"
        try:
            await self.master_db[collection_name].drop()
        except:
            pass
        
        # Delete from Master DB
        await self.master_db.organizations.delete_one({"name": organization_name})
        
        # Delete Admin
        await self.master_db.admins.delete_one({"email": current_admin_email})
        
        return {"status": "success", "message": "Organization deleted"}
