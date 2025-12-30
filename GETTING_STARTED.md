# BuildPro Bootstrap - Getting Started

## ✅ Bootstrap Complete!

Your BuildPro monorepo has been successfully created with the following structure:

```
BuildPro/
├── apps/
│   ├── web/              # Next.js 14 App Router + TypeScript + Tailwind
│   └── api/              # FastAPI + Python 3.12
├── packages/
│   ├── types/            # Shared TypeScript types (Zod schemas)
│   └── openapi/          # OpenAPI schema artifacts
├── .husky/               # Pre-commit hooks
├── .vscode/              # VS Code configuration
├── docker-compose.yml    # Local PostgreSQL + Redis
└── (config files)
```

## 🎯 Next Steps

### 1. Start Local Services (PostgreSQL + Redis)

```bash
# Start database and cache
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 2. Setup Python Environment

```bash
cd apps/api

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Return to root
cd ../..
```

### 3. Configure Environment Variables

```bash
# Copy example files
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env

# Edit with your values (especially auth provider)
```

**Minimum required for local dev:**

`apps/web/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`apps/api/.env`:
```env
DATABASE_URL=postgresql://buildpro:buildpro@localhost:5432/buildpro
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-me
ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Run Development Servers

**Terminal 1 - Web:**
```bash
pnpm dev:web
# → http://localhost:3000
```

**Terminal 2 - API:**
```bash
cd apps/api
source venv/bin/activate
make dev
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger UI)
```

### 5. Verify Installation

Visit:
- ✅ Web: http://localhost:3000
- ✅ API Health: http://localhost:8000/health
- ✅ API Docs: http://localhost:8000/docs

## 📦 What's Included

### Web App (`apps/web`)
- ✅ Next.js 14 with App Router
- ✅ TypeScript + strict mode
- ✅ Tailwind CSS + shadcn/ui setup
- ✅ ESLint + Prettier configured
- ✅ `.env.example` with Clerk + Supabase options

### API (`apps/api`)
- ✅ FastAPI with async support
- ✅ Python 3.12 with type hints
- ✅ Pydantic settings management
- ✅ SQLAlchemy + Alembic ready (setup in Prompt 1)
- ✅ Ruff + Black configured
- ✅ pytest setup with example test
- ✅ Makefile for common tasks
- ✅ `.env.example` with all required vars

### Shared Packages
- ✅ `@buildpro/types`: Comprehensive Zod schemas
  - Domain models (Tenant, User, Project, Material, Schedule, Report)
  - API types (Pagination, Responses)
  - Enums (UserRole, ProjectStatus, MaterialCategory, etc.)
- ✅ `@buildpro/openapi`: OpenAPI schema placeholder

### Tooling
- ✅ pnpm workspace configuration
- ✅ Root scripts for parallel dev, lint, test
- ✅ ESLint + Prettier for TypeScript
- ✅ Ruff + Black for Python
- ✅ Husky + lint-staged pre-commit hooks
- ✅ Docker Compose for local services
- ✅ VS Code recommended extensions + settings

## 🧪 Test the Setup

```bash
# Test TypeScript linting
pnpm lint

# Test formatting
pnpm format:check

# Test type checking
pnpm typecheck

# Test API (after starting server)
cd apps/api
source venv/bin/activate
make test
```

## 🔍 Project Standards

### Multi-tenant Safe
All code is designed for multi-tenant architecture:
- Tenant ID on all scoped tables
- Request middleware for tenant context
- RBAC enforcement (roles defined in `@buildpro/types`)

### Type Safety
- TypeScript strict mode enabled
- Shared types in `@buildpro/types`
- Pydantic models in API
- Zod validation on frontend

### Code Quality
- Pre-commit hooks prevent bad commits
- Consistent formatting (Prettier/Black)
- Linting catches common issues
- Tests required for core logic

## 📚 Ready for Prompt 1

You're now ready to proceed with **Prompt 1: Data model + Postgres + migrations**

The foundation is set with:
- ✅ Monorepo structure
- ✅ Development tooling
- ✅ Type definitions for all domain entities
- ✅ FastAPI app with config management
- ✅ Docker services for local development

### Quick Reference: Key Files

| Purpose | Location |
|---------|----------|
| Web routing | `apps/web/app/` |
| API routes | `apps/api/app/main.py` (add routers here) |
| Shared types | `packages/types/src/` |
| API config | `apps/api/app/core/config.py` |
| Database models | `apps/api/app/models/` (to be created) |
| Alembic migrations | `apps/api/alembic/` (to be created in Prompt 1) |

## 🚀 Development Tips

1. **Always activate Python venv** before working on API
2. **Use `pnpm` not `npm`** for package management
3. **Pre-commit hooks** will auto-fix many issues
4. **Check the docs** at http://localhost:8000/docs when API is running
5. **Use shared types** from `@buildpro/types` in web app

## 🐛 Common Issues

**"pnpm command not found"**
```bash
npm install -g pnpm
```

**"Cannot connect to database"**
```bash
docker-compose up -d postgres
# Wait a few seconds for startup
```

**"Python command not found"**
```bash
# Use python3.12 explicitly
python3.12 -m venv venv
```

**"Port already in use"**
```bash
# Check what's using the port
lsof -i :3000  # or :8000
# Kill the process or change port in .env
```

---

**Happy Building! 🏗️**

Need help? Check the main [README.md](../README.md) for detailed documentation.
