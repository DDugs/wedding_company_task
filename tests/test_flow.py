import pytest
from httpx import AsyncClient
from app.main import app
import asyncio

@pytest.mark.asyncio
async def test_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        
        # 1. Create Organization
        org_data = {
            "organization_name": "test_org_1",
            "email": "admin@testorg.com",
            "password": "securepassword"
        }
        response = await ac.post("/org/create", json=org_data)
        if response.status_code == 400 and "already exists" in response.text:
             pass
        else:
            assert response.status_code == 200
            data = response.json()
            assert data["organization_name"] == "test_org_1"
            assert data["collection_name"] == "org_test_org_1"

        # 2. Login
        login_data = {
            "email": "admin@testorg.com",
            "password": "securepassword"
        }
        response = await ac.post("/admin/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get Organization
        response = await ac.get("/org/get?organization_name=test_org_1")
        assert response.status_code == 200
        assert response.json()["organization_name"] == "test_org_1"

        # 4. Update Organization
        update_data = {
            "organization_name": "test_org_updated",
            "email": "admin@testorg.com", # Keep same
            "password": "" # Keep same
        }
        response = await ac.put("/org/update", json=update_data, headers=headers)
        assert response.status_code == 200

        # Verify Update
        response = await ac.get("/org/get?organization_name=test_org_updated")
        assert response.status_code == 200
        assert response.json()["collection_name"] == "org_test_org_updated"
        login_data["email"] = "admin@testorg.com"
        response = await ac.post("/admin/login", json=login_data)
        assert response.status_code == 200
        new_token = response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        response = await ac.delete("/org/delete?organization_name=test_org_updated", headers=new_headers)
        assert response.status_code == 200

