# BuildPro - Construction Management Platform

A comprehensive multi-tenant construction management platform for tracking projects, materials, schedules, and generating reports.

## 🏗️ Features

### Multi-Tenant Architecture
- **Tenant Isolation**: Strict data isolation with middleware-enforced scoping
- **RBAC System**: 6 role levels (OWNER, ADMIN, PM, SUPERVISOR, ESTIMATOR, SUB)
- **Audit Logging**: Complete audit trail for all CUD operations

### Project Management
- **Build Projects**: Manage multiple construction projects with lots
- **Materials & Takeoff**: Track material line items with quantity calculations
- **Schedule Management**: Milestone-based scheduling with Gantt view
- **Build Archive**: Search and compare completed projects
- **Project Cloning**: Use past projects as templates

### Calculations Engine
- **Server-Side Enforcement**: All calculations computed on backend
- **Decimal Precision**: Financial-grade accuracy with `ROUND_HALF_UP`
- **Supported Calculations**:
  - Floor area (length × width)
  - Volume (length × width × height)
  - Total quantity with wastage factor
  - Material costs (quantity × unit cost)
  - Cost per square foot
  - Earned value (budget × % complete)
  - Schedule variance in days

### Reports & Export
- **Report Types**: Progress, Budget vs Actual, Takeoff Summary, O&M Binder
- **Export Formats**: CSV, PDF (via ReportLab)
- **Bulk Import**: CSV import for materials and schedule data

### File Storage
- **S3 Integration**: Presigned URLs for secure uploads/downloads
- **File Metadata**: Track file type, size, and associations

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.108.0
- **Database**: PostgreSQL with SQLAlchemy 2.0.25 ORM
- **Migrations**: Alembic 1.13.1
- **Auth**: Clerk JWT validation via python-jose
- **Validation**: Pydantic schemas
- **Testing**: pytest with 40+ calculation tests

### Frontend
- **Framework**: Next.js 14 App Router
- **Language**: TypeScript 5.3.3 (strict mode)
- **Styling**: Tailwind CSS 3.4.1
- **Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React

## 📁 Project Structure

```
BuildPro/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   └── app/
│   │       ├── models/         # SQLAlchemy models (9 tables)
│   │       ├── schemas/        # Pydantic schemas
│   │       ├── api/            # API routers (7 routers)
│   │       ├── middleware/     # Tenant + RBAC middleware
│   │       ├── auth/           # JWT validation
│   │       ├── utils/          # Calculations, audit, import/export
│   │       ├── db/             # Database connection
│   │       └── main.py         # FastAPI app entrypoint
│   └── web/                    # Next.js frontend
│       ├── app/
│       │   └── (app)/         # Authenticated routes
│       │       ├── dashboard/
│       │       ├── projects/
│       │       ├── archive/
│       │       └── reports/
│       ├── components/
│       │   ├── ui/            # shadcn/ui components
│       │   └── layout/        # Sidebar, Header, AppLayout
│       └── lib/
│           ├── api-client.ts  # Type-safe API wrapper
│           ├── utils.ts       # Formatting utilities
│           └── csv-utils.ts   # CSV parsing/export
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.12+
- PostgreSQL 14+
- Clerk account (or configure alternative auth)

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd apps/api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and auth credentials
   ```

   Required environment variables:
   ```env
   DATABASE_URL=postgresql://user:pass@localhost:5432/buildpro
   CLERK_SECRET_KEY=your_clerk_secret_key
   JWT_ALGORITHM=RS256
   CORS_ORIGINS=http://localhost:3000
   S3_BUCKET=your-bucket-name
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API will be available at `http://localhost:8000`
   API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd apps/web
   pnpm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local
   ```

   Required environment variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   CLERK_SECRET_KEY=your_clerk_secret_key
   ```

3. **Start development server:**
   ```bash
   pnpm dev
   ```

   App will be available at `http://localhost:3000`

## 📊 Database Schema

### Core Tables
- **tenants**: Organization/company records
- **users**: User accounts
- **memberships**: User-tenant associations with roles
- **build_projects**: Construction project records
- **lots**: Individual lots within projects
- **material_line_items**: Material quantities and costs
- **schedule_milestones**: Project schedule phases
- **reports**: Generated report metadata
- **files**: File upload metadata
- **audit_logs**: Audit trail for all operations

### Key Indexes
- `(tenant_id, project_id)` on all multi-tenant tables
- `(tenant_id, deleted_at)` for soft delete queries
- `(user_id, tenant_id)` on memberships

## 🔐 Authentication & Authorization

### JWT Flow
1. User authenticates with Clerk (or configured provider)
2. Frontend receives JWT token
3. Token sent in `Authorization: Bearer <token>` header
4. Backend validates JWT and extracts `tenant_id` and `user_id`
5. Middleware sets `request.state.tenant_id` and `request.state.user_id`
6. All queries automatically scoped to tenant

### Role Hierarchy
```
OWNER (6)      → Full access, manage billing
ADMIN (5)      → Manage users, all data
PM (4)         → Manage projects
SUPERVISOR (3) → Edit materials, schedules
ESTIMATOR (2)  → View/edit estimates
SUB (1)        → View-only access
```

## 📝 API Endpoints

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Soft delete project
- `POST /api/projects/{id}/clone` - Clone project as template

### Materials
- `GET /api/materials` - List materials (filterable by project)
- `POST /api/materials` - Create material
- `PATCH /api/materials/{id}` - Update material
- `DELETE /api/materials/{id}` - Delete material
- `POST /api/materials/import-csv/{project_id}` - Bulk import from CSV
- `GET /api/materials/export-csv/{project_id}` - Export to CSV
- `GET /api/materials/summary/{project_id}` - Cost summary by category

### Schedule
- `GET /api/schedule` - List milestones
- `POST /api/schedule` - Create milestone
- `PATCH /api/schedule/{id}` - Update milestone
- `DELETE /api/schedule/{id}` - Delete milestone
- `GET /api/schedule/variance/{project_id}` - Schedule variance analysis

### Reports
- `POST /api/reports/generate` - Generate report (async)
- `GET /api/reports/{id}` - Get report metadata
- `GET /api/reports` - List reports

### Archive
- `GET /api/archive/search` - Search completed projects
- `GET /api/archive/compare` - Compare multiple projects

### Files
- `POST /api/files/upload-url` - Get presigned upload URL
- `POST /api/files` - Save file metadata
- `GET /api/files/{id}/download-url` - Get presigned download URL

## 🧪 Testing

### Backend Tests
```bash
cd apps/api
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Calculation Tests
All calculation functions have comprehensive test coverage:
- Edge cases (zero values, negative inputs)
- Decimal precision (financial calculations)
- Rounding behavior (`ROUND_HALF_UP`)
- Error handling

Example test run:
```
tests/test_calculations.py::test_floor_area PASSED
tests/test_calculations.py::test_total_cost_precision PASSED
tests/test_calculations.py::test_wastage_calculation PASSED
```

## 📈 Development Roadmap

### ✅ Completed
- [x] Database models with multi-tenancy
- [x] RBAC middleware and auth integration
- [x] Core API endpoints (projects, materials, schedule)
- [x] Calculation engine with tests
- [x] Frontend layout and navigation
- [x] Dashboard with KPI cards
- [x] Projects list and detail pages
- [x] Materials table with calculations
- [x] Schedule milestones view
- [x] Archive search interface
- [x] Reports listing
- [x] CSV import/export for materials

### 🚧 In Progress
- [ ] Celery + Redis for async report generation
- [ ] ReportLab PDF templates for 4 report types
- [ ] Gantt chart visualization for schedule
- [ ] Material bulk edit with inline table editor

### 📋 Planned
- [ ] XLSX import/export (in addition to CSV)
- [ ] OpenTelemetry instrumentation
- [ ] Rate limiting per tenant
- [ ] Audit log viewer UI (admin only)
- [ ] GitHub Actions CI/CD pipeline
- [ ] Docker containers for deployment
- [ ] Deployment docs (Vercel + Railway/Render)

## 🔧 Configuration

### Calculation Precision
All financial calculations use `Decimal` type with `ROUND_HALF_UP`:
```python
from decimal import Decimal, ROUND_HALF_UP

def total_cost(quantity: Decimal, unit_cost: Decimal) -> Decimal:
    return (quantity * unit_cost).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
```

### Multi-Tenant Queries
All queries automatically scope to tenant via middleware:
```python
# Middleware sets request.state.tenant_id
tenant_id = request.state.tenant_id

# All queries filtered by tenant
materials = db.query(MaterialLineItem).filter(
    MaterialLineItem.tenant_id == tenant_id
).all()
```

## 📄 License

Proprietary - All rights reserved

## 👥 Contributors

Built with GitHub Copilot

---

**Need help?** Check the API docs at `/docs` or review the test suite for usage examples.

Multi-tenant construction project management platform with Next.js frontend and FastAPI backend.

## 🏗️ Architecture

This is a pnpm monorepo with the following structure:

```
BuildPro/
├── apps/
│   ├── web/          # Next.js 14 App Router (TypeScript)
│   └── api/          # FastAPI backend (Python 3.12)
├── packages/
│   ├── types/        # Shared TypeScript types
│   └── openapi/      # OpenAPI schema artifacts
└── (config files)
```

## 📋 Prerequisites

- **Node.js**: >= 18.0.0 (use `.nvmrc` file)
- **pnpm**: >= 8.0.0
- **Python**: 3.12
- **PostgreSQL**: >= 14
- **Redis**: >= 6

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install pnpm if you haven't already
npm install -g pnpm

# Install Node dependencies
pnpm install

# Install Python dependencies
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cd ../..
```

### 2. Setup Environment Variables

```bash
# Copy example env files
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env

# Edit the files with your actual values
```

**Required environment variables:**

**`apps/web/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Choose one auth provider:
# Option A: Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Option B: Supabase
# NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

**`apps/api/.env`:**
```env
DATABASE_URL=postgresql://buildpro:buildpro@localhost:5432/buildpro
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Setup Local Database

```bash
# Create PostgreSQL database
createdb buildpro

# Or using psql:
psql -U postgres -c "CREATE DATABASE buildpro;"
psql -U postgres -c "CREATE USER buildpro WITH PASSWORD 'buildpro';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE buildpro TO buildpro;"
```

### 4. Run Development Servers

**Option A: Run all services (parallel)**
```bash
pnpm dev
```

**Option B: Run services individually**

Terminal 1 - Web (Next.js):
```bash
pnpm dev:web
# Runs on http://localhost:3000
```

Terminal 2 - API (FastAPI):
```bash
cd apps/api
source venv/bin/activate  # Activate venv first
make dev
# Or: ./scripts/dev.sh
# Runs on http://localhost:8000
```

### 5. Access the Applications

- **Web App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Swagger)
- **API ReDoc**: http://localhost:8000/redoc
- **API Health**: http://localhost:8000/health

## 🛠️ Development Workflow

### Linting & Formatting

```bash
# Lint all code
pnpm lint

# Fix linting issues
pnpm lint:fix

# Format all code
pnpm format

# Check formatting without changes
pnpm format:check
```

### Type Checking

```bash
# Type check all TypeScript
pnpm typecheck

# Type check only web
pnpm --filter web typecheck
```

### Testing

```bash
# Run all tests
pnpm test

# Run only API tests
pnpm test:python
# Or: cd apps/api && pytest
```

### Database Migrations (Alembic)

```bash
cd apps/api

# Create a new migration
make migrate msg="Add users table"

# Run migrations
make upgrade

# Rollback migration
alembic downgrade -1
```

## 📦 Package Scripts

### Root (`/`)
- `pnpm dev` - Run all services in parallel
- `pnpm build` - Build all apps
- `pnpm lint` - Lint TypeScript and Python
- `pnpm format` - Format all code
- `pnpm test` - Run all tests
- `pnpm clean` - Clean all node_modules and build artifacts

### Web App (`apps/web/`)
- `pnpm dev` - Start Next.js dev server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Lint Next.js app

### API (`apps/api/`)
- `make dev` - Start FastAPI dev server
- `make migrate` - Create new migration
- `make upgrade` - Run migrations
- `make test` - Run pytest
- `make lint` - Run ruff + black check
- `make format` - Format Python code

## 🔒 Pre-commit Hooks

Pre-commit hooks are automatically installed via husky when you run `pnpm install`.

They will:
- Lint and format TypeScript/JavaScript files
- Lint and format Python files
- Check for common issues (trailing whitespace, merge conflicts, etc.)

**Manual setup (if needed):**
```bash
# Install husky hooks
pnpm prepare

# Optional: Use pre-commit for Python hooks
pip install pre-commit
pre-commit install
```

## 🏗️ Multi-tenant Architecture

This application enforces strict tenant isolation:

1. **All tenant-scoped tables include `tenant_id`**
2. **API middleware extracts tenant context from JWT**
3. **All queries are automatically scoped to the current tenant**
4. **RBAC roles**: OWNER, ADMIN, PM, SUPERVISOR, ESTIMATOR, SUB

## 📚 Tech Stack

### Frontend (`apps/web`)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **Auth**: Clerk or Supabase Auth
- **State**: React hooks + context
- **API Client**: Fetch wrapper with types from `@buildpro/types`

### Backend (`apps/api`)
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Database**: PostgreSQL + SQLAlchemy
- **Migrations**: Alembic
- **Cache/Jobs**: Redis + Celery
- **Auth**: JWT validation (Clerk or Supabase)
- **Storage**: S3-compatible (AWS S3 / Cloudflare R2)
- **Reports**: ReportLab (PDF generation)
- **Testing**: pytest

### Shared (`packages/`)
- **types**: Zod schemas + TypeScript types for domain models
- **openapi**: OpenAPI schema artifacts (generated from FastAPI)

## 🌍 Production Deployment

### Recommended Stack

- **Web**: Vercel (zero-config Next.js deployment)
- **API**: Render, Railway, or Fly.io
- **Database**: Supabase, AWS RDS, or Neon
- **Redis**: Upstash or Redis Cloud
- **Storage**: AWS S3 or Cloudflare R2

### Environment Checklist

- [ ] Set strong `SECRET_KEY` for API
- [ ] Configure production database with SSL
- [ ] Set up Redis with authentication
- [ ] Configure CORS `ALLOWED_ORIGINS` to production domains
- [ ] Set up S3/R2 bucket with proper permissions
- [ ] Configure auth provider (Clerk or Supabase) for production
- [ ] Enable SSL/TLS for all services
- [ ] Set up monitoring and error tracking
- [ ] Configure backup strategy for database

## 🐛 Troubleshooting

### pnpm install fails
```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### API won't start
```bash
# Check Python virtual environment is activated
source apps/api/venv/bin/activate

# Verify environment variables
cat apps/api/.env

# Check database connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Database migration errors
```bash
cd apps/api
# Reset to a known state
alembic downgrade base
alembic upgrade head
```

## 📖 Additional Documentation

- [API Development Guide](apps/api/README.md) *(to be created)*
- [Web Development Guide](apps/web/README.md) *(to be created)*
- [Contributing Guidelines](CONTRIBUTING.md) *(to be created)*
- [Deployment Guide](DEPLOYMENT.md) *(to be created)*

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

---

**Built with ❤️ for construction teams**