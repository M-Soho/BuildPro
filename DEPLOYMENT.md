# BuildPro Deployment Guide

This guide covers deploying BuildPro to production using modern cloud services.

## Deployment Architecture

**Recommended Stack:**
- **Frontend**: Vercel (Next.js)
- **Backend API**: Railway or Render
- **Database**: Supabase PostgreSQL or AWS RDS
- **File Storage**: AWS S3 or R2 (Cloudflare)
- **Task Queue**: Redis Cloud (Upstash)
- **Auth**: Clerk

## Prerequisites

- GitHub repository with your code
- Accounts: Vercel, Railway/Render, Supabase/AWS
- Domain name (optional, for custom domains)

## 1. Database Setup

### Option A: Supabase (Recommended for prototypes)

1. Create project at [supabase.com](https://supabase.com)
2. Note your connection string from Settings > Database
3. Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`

### Option B: AWS RDS (Recommended for production)

1. Create PostgreSQL 14+ instance in AWS RDS console
2. Configure security group to allow inbound on port 5432
3. Note connection details (host, port, database, user, password)

## 2. Backend API Deployment

### Railway Deployment

1. **Create Railway project:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   cd apps/api
   railway init
   ```

2. **Configure environment variables:**
   Go to Railway dashboard > Variables and add:
   ```env
   DATABASE_URL=your_supabase_or_rds_connection_string
   CLERK_SECRET_KEY=your_clerk_secret
   JWT_ALGORITHM=RS256
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   S3_BUCKET=your-s3-bucket
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=us-east-1
   REDIS_URL=your_redis_url
   ```

3. **Create railway.json:**
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
       "healthcheckPath": "/health",
       "healthcheckTimeout": 100
     }
   }
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

### Render Deployment

1. **Create new Web Service** at [render.com](https://render.com)
2. **Connect GitHub repo**
3. **Configure:**
   - Build Command: `pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: (same as Railway above)

## 3. Frontend Deployment

### Vercel Deployment

1. **Connect repository:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select `apps/web` as root directory

2. **Configure build settings:**
   - Framework Preset: Next.js
   - Build Command: `pnpm build`
   - Output Directory: `.next`
   - Install Command: `pnpm install`

3. **Environment variables:**
   ```env
   NEXT_PUBLIC_API_URL=https://your-api-domain.railway.app
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_your_clerk_key
   CLERK_SECRET_KEY=sk_live_your_clerk_secret
   ```

4. **Deploy:**
   - Click "Deploy"
   - Vercel will auto-deploy on every push to main branch

## 4. Database Migration

**Run migrations on production:**

```bash
# Set production DATABASE_URL
export DATABASE_URL=your_production_db_url

# Run migrations
cd apps/api
alembic upgrade head
```

Or configure Railway/Render to run migrations on deploy (see railway.json above).

## 5. File Storage (AWS S3)

1. **Create S3 bucket:**
   ```bash
   aws s3 mb s3://buildpro-production-files
   ```

2. **Configure CORS:**
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST"],
       "AllowedOrigins": ["https://your-frontend-domain.vercel.app"],
       "ExposeHeaders": ["ETag"]
     }
   ]
   ```

3. **Create IAM user with S3 access:**
   - Policy: `AmazonS3FullAccess` (or custom policy)
   - Note Access Key ID and Secret Access Key

## 6. Redis Setup (for Celery)

### Upstash Redis (Recommended)

1. Create database at [upstash.com](https://upstash.com)
2. Copy Redis URL (format: `redis://...`)
3. Add to backend environment variables as `REDIS_URL`

## 7. Authentication (Clerk)

1. **Configure production instance:**
   - Go to Clerk dashboard
   - Create production instance (separate from development)
   - Add production domain to allowed origins

2. **Configure JWT template:**
   - Go to JWT Templates in Clerk dashboard
   - Add custom claims:
     ```json
     {
       "tenant_id": "{{user.public_metadata.tenant_id}}",
       "role": "{{user.public_metadata.role}}"
     }
     ```

3. **Update environment variables:**
   - Use production Clerk keys (`pk_live_...` and `sk_live_...`)

## 8. Monitoring & Observability

### Sentry (Error Tracking)

1. **Create Sentry project:**
   - Frontend: Next.js
   - Backend: Python/FastAPI

2. **Install SDK:**
   ```bash
   # Frontend
   cd apps/web
   pnpm add @sentry/nextjs
   
   # Backend
   cd apps/api
   pip install sentry-sdk[fastapi]
   ```

3. **Configure:**
   ```typescript
   // apps/web/sentry.client.config.ts
   import * as Sentry from "@sentry/nextjs";
   
   Sentry.init({
     dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
     environment: process.env.NODE_ENV,
   });
   ```

   ```python
   # apps/api/app/main.py
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration
   
   sentry_sdk.init(
       dsn=os.getenv("SENTRY_DSN"),
       integrations=[FastApiIntegration()],
   )
   ```

### Logging

**Structured JSON logging:**
```python
# apps/api/app/utils/logging.py
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "tenant_id"):
            log_obj["tenant_id"] = record.tenant_id
        if hasattr(record, "user_id"):
            log_obj["user_id"] = record.user_id
        return json.dumps(log_obj)
```

## 9. CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd apps/api
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd apps/api
          pytest --cov=app
  
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      
      - name: Install dependencies
        run: |
          cd apps/web
          pnpm install
      
      - name: Build
        run: |
          cd apps/web
          pnpm build
```

## 10. Post-Deployment Checklist

- [ ] Run database migrations
- [ ] Test authentication flow
- [ ] Verify tenant isolation (create test tenants)
- [ ] Test file uploads to S3
- [ ] Verify API endpoints return correct data
- [ ] Test RBAC permissions for each role
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate (auto with Vercel/Railway)
- [ ] Enable monitoring dashboards (Sentry, Vercel Analytics)
- [ ] Configure backups for database
- [ ] Set up alerting for errors/downtime
- [ ] Document API with Swagger/OpenAPI
- [ ] Create admin user for first tenant

## 11. Scaling Considerations

### Database
- Enable connection pooling (pgBouncer)
- Add read replicas for heavy read workloads
- Implement query caching (Redis)
- Partition large tables by tenant_id

### API
- Scale horizontally (multiple Railway/Render instances)
- Add rate limiting per tenant
- Implement caching for expensive queries
- Use CDN for static assets

### Frontend
- Vercel handles CDN and edge caching automatically
- Implement ISR (Incremental Static Regeneration) for reports
- Use React.lazy() for code splitting

### Background Jobs
- Scale Celery workers independently
- Use separate queues for different task types
- Monitor queue depth and worker health

## Troubleshooting

### Database connection errors
```bash
# Test connection
psql $DATABASE_URL

# Check for connection limits
SELECT count(*) FROM pg_stat_activity;
```

### CORS errors
- Verify `CORS_ORIGINS` includes your frontend domain
- Check for trailing slashes (match exactly)
- Ensure protocol matches (http vs https)

### Auth errors
- Verify JWT secret matches between Clerk and backend
- Check JWT expiration time
- Ensure custom claims are configured in Clerk

### File upload errors
- Verify S3 bucket CORS configuration
- Check IAM permissions for presigned URL generation
- Test presigned URLs manually with curl

---

**Production ready!** 🚀 Monitor your dashboards and set up alerts for critical errors.
