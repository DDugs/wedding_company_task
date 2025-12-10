import asyncio
import httpx
import sys

async def verify():
    base_url = "http://127.0.0.1:8000"
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        print("1. Creating Organization...")
        org_data = {
            "organization_name": "verify_org_1",
            "email": "admin@verify.com",
            "password": "secure"
        }
        resp = await client.post("/org/create", json=org_data)
        if resp.status_code == 400 and "already exists" in resp.text:
            print("   Organization already exists. Attempting to proceed with login.")
        elif resp.status_code == 200:
            print("   Success:", resp.json())
        else:
            print(f"   Failed: {resp.status_code} {resp.text}")
            return

        print("\n2. Admin Login...")
        login_data = {
            "email": "admin@verify.com",
            "password": "secure"
        }
        resp = await client.post("/admin/login", json=login_data)
        if resp.status_code != 200:
            print(f"   Login Failed: {resp.status_code} {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print("   Login Success. Token received.")
        headers = {"Authorization": f"Bearer {token}"}

        print("\n3. Get Organization...")
        resp = await client.get("/org/get?organization_name=verify_org_1")
        if resp.status_code == 200:
            print("   Success:", resp.json())
        else:
             print(f"   Failed: {resp.status_code} {resp.text}")

        print("\n4. Update Organization...")
        update_data = {
            "organization_name": "verify_org_new",
            "email": "admin@verify.com",
            "password": ""
        }
        resp = await client.put("/org/update", json=update_data, headers=headers)
        if resp.status_code == 200:
             print("   Update Success.")
        else:
             print(f"   Update Failed: {resp.status_code} {resp.text}")
             if resp.status_code != 200: return
        print("\n5. Get New Organization...")
        resp = await client.get("/org/get?organization_name=verify_org_new")
        if resp.status_code == 200:
            print("   Success:", resp.json())
        else:
             print(f"   Failed to get new org: {resp.status_code} {resp.text}")

        print("\n6. Delete Organization...")
        resp = await client.post("/admin/login", json=login_data)
        new_token = resp.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        resp = await client.delete("/org/delete?organization_name=verify_org_new", headers=new_headers)
        if resp.status_code == 200:
            print("   Delete Success.")
        else:
            print(f"   Delete Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    asyncio.run(verify())
