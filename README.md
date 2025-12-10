# Organization Management Service

A FastAPI-based backend service for managing organizations in a multi-tenant architecture using MongoDB.

## Features
- **Multi-tenancy**: Dedicated MongoDB collection for each organization (`org_<name>`).
- **Authentication**: Admin login with JWT tokens and bcrypt password hashing.
- **Organization Management**: Create, Read, Update (with rename), and Delete organizations.
- **Architecture**: Modular, class-based Service Layer design.

## Prerequisites
- **Python 3.10+**
- **MongoDB** running locally on port `27017` OR accessible via connection string.

## Installation

1. **Clone the repository** (or navigate to directory).
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Setup**:
   Run `docker run -d -p 27017:27017 --name mongodb mongo:latest`
   Ensure MongoDB is at `mongodb://localhost:27017`.

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## API Documentation
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Usage
1. Create a New Organization
This creates the organization and the admin account.

```bash
curl -X POST "URL/org/create" ^
     -H "Content-Type: application/json" ^
     -d "{\"organization_name\": \"MyWedding\", \"email\": \"admin@wedding.com\", \"password\": \"secret123\"}"
```

2. Login as Admin
Use the credentials you just created to get an access token.

```bash
curl -X POST "URL/admin/login" ^
     -H "Content-Type: application/json" ^
     -d "{\"email\": \"admin@wedding.com\", \"password\": \"secret123\"}"
```
Copy the access_token from the response for the next steps.

3. Get Organization Details
```bash
curl "URL/org/get?organization_name=MyWedding"
```

4. Update Organization (Requires Token)
Replace YOUR_TOKEN_HERE with the token from step 2.
```bash
curl -X PUT "URL/org/update" ^
     -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
     -H "Content-Type: application/json" ^
     -d "{\"organization_name\": \"MyWeddingUpdated\", \"email\": \"admin@wedding.com\", \"password\": \"newpassword123\"}"
```

5. Delete Organization (Requires Token)
Note: Since we updated the name in the previous step, use the new name if that succeeded, otherwise use the old name. Also, if you changed the password, your old token is still valid until it expires, but for a real test you might want to login again with the new password.
```bash
curl -X DELETE "URL/org/delete?organization_name=MyWeddingUpdated" ^
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Project Structure
```
app/
├── main.py            # Application entry point
├── database.py        # Database connection & helpers
├── models.py          # Pydantic models
├── utils.py           # Security utilities (Hash, JWT)
├── routes/
│   ├── auth.py        # Authentication endpoints
│   └── organization.py# Organization CRUD endpoints
└── services/
    ├── auth_service.py # Auth business logic
    └── org_service.py  # Organization business logic
```
