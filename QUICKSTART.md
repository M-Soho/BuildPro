# BuildPro - Quick Start Guide

Get BuildPro running locally in under 10 minutes.

## Prerequisites

- **Node.js** 18+ and **pnpm** 8+
- **Python** 3.12+
- **PostgreSQL** 14+ (or use Docker)
- **Clerk Account** (free tier: https://clerk.com)

## Quick Setup

### 1. Clone and Install

```bash
# Clone the repository
cd /path/to/BuildPro

# Install frontend dependencies
cd apps/web
pnpm install

# Install backend dependencies
cd ../api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

**Option A: Local PostgreSQL**
```bash
# Create database
createdb buildpro

# Or using psql
psql -U postgres
CREATE DATABASE buildpro;
\q
```

**Option B: Docker PostgreSQL**
```bash
docker run --name buildpro-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=buildpro \
  -p 5432:5432 \
  -d postgres:14
```

### 3. Configure Environment Variables

**Backend (.env):**
```bash
cd apps/api
cp .env.example .env
# Edit .env with your values
```

Minimum required:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/buildpro
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key
JWT_ALGORITHM=RS256
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env.local):**
```bash
cd apps/web
cp .env.local.example .env.local
# Edit .env.local
```

Minimum required:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key
```

### 4. Set Up Clerk Authentication

1. **Create Clerk Application:**
   - Go to https://dashboard.clerk.com
   - Create new application
   - Select "Email" and "Password" as authentication methods

2. **Get API Keys:**
   - Go to API Keys in Clerk dashboard
   - Copy "Publishable key" → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - Copy "Secret key" → `CLERK_SECRET_KEY`

3. **Configure JWT Template:**
   - Go to "JWT Templates" in Clerk
   - Create new template named "buildpro"
   - Add custom claims:
   ```json
   {
     "tenant_id": "{{user.public_metadata.tenant_id}}",
     "role": "{{user.public_metadata.role}}"
   }
   ```
   - Save and set as default

### 5. Run Database Migrations

```bash
cd apps/api
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt"
```

You should see 9 tables:
- tenants
- users  
- memberships
- build_projects
- lots
- material_line_items
- schedule_milestones
- reports
- files
- audit_logs

### 6. Start Backend API

```bash
cd apps/api
source venv/bin/activate

# Start dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 7. Start Frontend

```bash
cd apps/web
pnpm dev
```

App runs at: http://localhost:3000

## First-Time Setup

### Create Your First Tenant

1. **Sign up via Clerk:**
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Create account with email/password

2. **Set tenant metadata via Clerk Dashboard:**
   - Go to Clerk Dashboard → Users
   - Find your user
   - Edit "Public metadata"
   - Add:
   ```json
   {
     "tenant_id": "tenant_123",
     "role": "OWNER"
   }
   ```
   - Save

3. **Create tenant in database:**
   ```bash
   psql $DATABASE_URL
   INSERT INTO tenants (id, name, slug, created_at, updated_at)
   VALUES ('tenant_123', 'My Company', 'my-company', NOW(), NOW());
   ```

### Create Test Data

**Via API (Swagger UI):**
1. Go to http://localhost:8000/docs
2. Click "Authorize" and paste your JWT token
3. Create project via `POST /api/projects`
4. Create materials via `POST /api/materials`

**Or use Python script:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}

# Create project
project = {
    "title": "Sunset Hills Phase 2",
    "description": "24-unit development",
    "address": "123 Main St, Austin, TX",
    "budget": 2500000,
    "home_area_sqft": 2800,
    "lot_width": 50,
    "lot_depth": 120,
}
response = requests.post(
    "http://localhost:8000/api/projects",
    json=project,
    headers=headers
)
project_id = response.json()["id"]

# Create material
material = {
    "project_id": project_id,
    "category": "FRAMING",
    "description": "2x4 Lumber - 8ft",
    "quantity": 500,
    "unit": "EA",
    "wastage_factor": 0.1,
    "unit_cost": 8.50,
}
requests.post(
    "http://localhost:8000/api/materials",
    json=material,
    headers=headers
)
```

## Verify Installation

### Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### API Test
```bash
# Get current user (requires auth token)
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Frontend Test
1. Open http://localhost:3000
2. Sign in with Clerk
3. Should see Dashboard with KPIs

## Troubleshooting

### Database Connection Errors
```bash
# Test connection
psql $DATABASE_URL

# Check if PostgreSQL is running
pg_ctl status

# Restart PostgreSQL
# macOS: brew services restart postgresql
# Linux: sudo systemctl restart postgresql
```

### Migration Errors
```bash
# Reset database (CAUTION: Deletes all data)
alembic downgrade base
alembic upgrade head

# Or drop and recreate
dropdb buildpro && createdb buildpro
alembic upgrade head
```

### CORS Errors
- Verify `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
- No trailing slashes
- Restart backend after changing .env

### Auth Errors
- Verify Clerk keys match in frontend and backend `.env` files
- Check JWT template is configured with custom claims
- Ensure user has `tenant_id` in public metadata

### Port Already in Use
```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

## Development Workflow

### Making Changes

**Backend:**
1. Edit code in `apps/api/app/`
2. Changes auto-reload (uvicorn --reload)
3. Run tests: `pytest`

**Frontend:**
1. Edit code in `apps/web/`
2. Changes hot-reload automatically
3. Build for production: `pnpm build`

### Creating Database Migration

```bash
cd apps/api

# Auto-generate migration
alembic revision --autogenerate -m "Add new field"

# Review generated file in alembic/versions/
# Edit if needed

# Apply migration
alembic upgrade head
```

### Running Tests

```bash
# Backend tests
cd apps/api
pytest
pytest --cov=app  # With coverage

# Frontend tests (when implemented)
cd apps/web
pnpm test
```

## Next Steps

1. **Explore the Dashboard:** http://localhost:3000/dashboard
2. **Create a Project:** Click "New Project"
3. **Add Materials:** Go to project → Materials tab → "Add Material"
4. **Import CSV:** Use "Import CSV" button with sample data
5. **Generate Report:** Go to Reports → "Generate Report"

## Sample Data

### Material CSV Template
```csv
category,description,quantity,unit,wastage_factor,unit_cost,vendor,notes
FRAMING,2x4 Lumber - 8ft,500,EA,0.10,8.50,ABC Lumber,Premium grade
CONCRETE,Ready Mix 3000 PSI,45,CY,0.05,125.00,XYZ Concrete,
DRYWALL,1/2" Drywall Sheet,200,EA,0.15,12.00,Drywall Pro,
```

Save as `materials.csv` and import via UI.

## Resources

- **API Documentation:** http://localhost:8000/docs
- **Clerk Dashboard:** https://dashboard.clerk.com
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Next.js Docs:** https://nextjs.org/docs

---

**You're all set!** 🎉 Start building construction projects with BuildPro.
