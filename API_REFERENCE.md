# BuildPro API Reference

Complete API documentation for BuildPro construction management platform.

**Base URL:** `http://localhost:8000` (development) or `https://api.buildpro.com` (production)

**Authentication:** All endpoints require JWT Bearer token (except `/health`)

```
Authorization: Bearer <your_jwt_token>
```

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Projects](#projects)
4. [Materials](#materials)
5. [Schedule](#schedule)
6. [Reports](#reports)
7. [Files](#files)
8. [Archive](#archive)
9. [Data Models](#data-models)
10. [Error Handling](#error-handling)

---

## Authentication

BuildPro uses JWT tokens for authentication. Tokens are issued by Clerk (or your configured provider).

### Get Token

**Frontend (Next.js with Clerk):**
```typescript
import { useAuth } from "@clerk/nextjs";

const { getToken } = useAuth();
const token = await getToken();
```

**Use in API calls:**
```typescript
fetch("/api/projects", {
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

### JWT Claims

Required claims in JWT payload:
```json
{
  "sub": "user_123",
  "tenant_id": "tenant_abc",
  "role": "OWNER"
}
```

---

## Users

### Get Current User

```http
GET /api/users/me
```

**Response:**
```json
{
  "id": "user_123",
  "email": "john@example.com",
  "name": "John Doe",
  "memberships": [
    {
      "tenant_id": "tenant_abc",
      "role": "OWNER"
    }
  ]
}
```

### Get User by ID

```http
GET /api/users/{user_id}
```

**Path Parameters:**
- `user_id` (string) - User ID

**Response:**
```json
{
  "id": "user_123",
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### List Users

```http
GET /api/users?page=1&page_size=20
```

**Query Parameters:**
- `page` (integer, optional) - Page number (default: 1)
- `page_size` (integer, optional) - Items per page (default: 20, max: 100)

**Response:**
```json
{
  "items": [
    {
      "id": "user_123",
      "email": "john@example.com",
      "name": "John Doe"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

## Projects

### List Projects

```http
GET /api/projects?status=ACTIVE&page=1&page_size=20
```

**Query Parameters:**
- `status` (string, optional) - Filter by status: `PLANNING`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `CANCELLED`
- `page` (integer, optional) - Page number
- `page_size` (integer, optional) - Items per page

**Response:**
```json
{
  "items": [
    {
      "id": "proj_123",
      "title": "Sunset Hills Phase 2",
      "description": "24-unit development",
      "address": "123 Main St, Austin, TX",
      "status": "ACTIVE",
      "budget": 2500000.00,
      "home_area_sqft": 2800.00,
      "lot_width": 50.00,
      "lot_depth": 120.00,
      "baseline_start_date": "2024-01-15",
      "baseline_end_date": "2024-12-31",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2024-01-10T15:30:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 20
}
```

### Create Project

```http
POST /api/projects
```

**Request Body:**
```json
{
  "title": "Mountain View Estates",
  "description": "Luxury homes with mountain views",
  "address": "456 Oak Ave, Denver, CO",
  "status": "PLANNING",
  "budget": 3200000,
  "home_area_sqft": 3200,
  "lot_width": 60,
  "lot_depth": 130,
  "baseline_start_date": "2024-03-01",
  "baseline_end_date": "2025-02-28"
}
```

**Response:** `201 Created`
```json
{
  "id": "proj_456",
  "title": "Mountain View Estates",
  ...
}
```

### Get Project

```http
GET /api/projects/{project_id}
```

**Response:**
```json
{
  "id": "proj_123",
  "title": "Sunset Hills Phase 2",
  "lots": [
    {
      "id": "lot_1",
      "lot_number": "101",
      "status": "ACTIVE",
      "notes": "Premium corner lot"
    }
  ],
  ...
}
```

### Update Project

```http
PATCH /api/projects/{project_id}
```

**Request Body:**
```json
{
  "status": "ON_HOLD",
  "notes": "Delayed due to permit issues"
}
```

**Response:** `200 OK`

### Delete Project (Soft Delete)

```http
DELETE /api/projects/{project_id}
```

**Response:** `204 No Content`

### Clone Project

```http
POST /api/projects/{project_id}/clone
```

**Request Body:**
```json
{
  "new_title": "Sunset Hills Phase 3",
  "clone_materials": true,
  "clone_schedule": true
}
```

**Response:** `201 Created`
```json
{
  "id": "proj_789",
  "title": "Sunset Hills Phase 3",
  ...
}
```

### Lot Endpoints

```http
GET /api/projects/{project_id}/lots
POST /api/projects/{project_id}/lots
PATCH /api/projects/{project_id}/lots/{lot_id}
DELETE /api/projects/{project_id}/lots/{lot_id}
```

---

## Materials

### List Materials

```http
GET /api/materials?project_id=proj_123&category=FRAMING
```

**Query Parameters:**
- `project_id` (string, required) - Filter by project
- `category` (string, optional) - Filter by category
- `page` (integer, optional)
- `page_size` (integer, optional)

**Response:**
```json
{
  "items": [
    {
      "id": "mat_1",
      "project_id": "proj_123",
      "category": "FRAMING",
      "description": "2x4 Lumber - 8ft",
      "quantity": 500.00,
      "unit": "EA",
      "wastage_factor": 0.10,
      "total_qty": 550.00,
      "unit_cost": 8.50,
      "total_cost": 4675.00,
      "vendor": "ABC Lumber",
      "notes": "Premium grade",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 24,
  "page": 1,
  "page_size": 20
}
```

### Create Material

```http
POST /api/materials
```

**Request Body:**
```json
{
  "project_id": "proj_123",
  "category": "CONCRETE",
  "description": "Ready Mix 3000 PSI",
  "quantity": 45,
  "unit": "CY",
  "wastage_factor": 0.05,
  "unit_cost": 125.00,
  "vendor": "XYZ Concrete",
  "notes": "Standard mix"
}
```

**Note:** `total_qty` and `total_cost` are calculated server-side.

**Response:** `201 Created`

### Update Material

```http
PATCH /api/materials/{material_id}
```

**Request Body:**
```json
{
  "quantity": 50,
  "unit_cost": 130.00
}
```

**Response:** `200 OK`

### Delete Material

```http
DELETE /api/materials/{material_id}
```

**Response:** `204 No Content`

### Import Materials from CSV

```http
POST /api/materials/import-csv/{project_id}
```

**Request:** `multipart/form-data`
- `file` (file) - CSV file

**CSV Format:**
```csv
category,description,quantity,unit,wastage_factor,unit_cost,vendor,notes
FRAMING,2x4 Lumber - 8ft,500,EA,0.10,8.50,ABC Lumber,Premium grade
CONCRETE,Ready Mix 3000 PSI,45,CY,0.05,125.00,XYZ Concrete,
```

**Response:**
```json
{
  "imported_count": 2,
  "skipped_count": 0,
  "errors": []
}
```

### Export Materials to CSV

```http
GET /api/materials/export-csv/{project_id}
```

**Response:** CSV file download

### Get Materials Summary

```http
GET /api/materials/summary/{project_id}
```

**Response:**
```json
{
  "total_cost": 125000.00,
  "by_category": [
    {
      "category": "FRAMING",
      "total_cost": 45000.00,
      "item_count": 15
    },
    {
      "category": "CONCRETE",
      "total_cost": 30000.00,
      "item_count": 8
    }
  ]
}
```

---

## Schedule

### List Milestones

```http
GET /api/schedule?project_id=proj_123
```

**Response:**
```json
{
  "items": [
    {
      "id": "mile_1",
      "project_id": "proj_123",
      "phase": "FOUNDATION",
      "description": "Foundation Complete",
      "baseline_start_date": "2024-01-15",
      "baseline_end_date": "2024-02-15",
      "actual_start_date": "2024-01-15",
      "actual_end_date": null,
      "status": "IN_PROGRESS",
      "notes": ""
    }
  ]
}
```

### Create Milestone

```http
POST /api/schedule
```

**Request Body:**
```json
{
  "project_id": "proj_123",
  "phase": "FRAMING",
  "description": "Framing Complete",
  "baseline_start_date": "2024-02-20",
  "baseline_end_date": "2024-03-30"
}
```

**Response:** `201 Created`

### Update Milestone

```http
PATCH /api/schedule/{milestone_id}
```

**Request Body:**
```json
{
  "actual_end_date": "2024-03-25",
  "status": "COMPLETED"
}
```

**Response:** `200 OK`

### Get Schedule Variance

```http
GET /api/schedule/variance/{project_id}
```

**Response:**
```json
{
  "project_id": "proj_123",
  "total_days_variance": -5,
  "milestones": [
    {
      "phase": "FOUNDATION",
      "baseline_duration_days": 31,
      "actual_duration_days": 28,
      "variance_days": -3,
      "status": "COMPLETED"
    }
  ]
}
```

---

## Reports

### Generate Report

```http
POST /api/reports/generate
```

**Request Body:**
```json
{
  "project_id": "proj_123",
  "report_type": "PROGRESS",
  "format": "PDF",
  "parameters": {
    "include_photos": true,
    "include_schedule": true
  }
}
```

**Report Types:**
- `PROGRESS` - Project progress report
- `BUDGET_VS_ACTUAL` - Budget comparison
- `TAKEOFF_SUMMARY` - Materials takeoff summary
- `OM_BINDER` - Operations & Maintenance binder

**Response:** `202 Accepted`
```json
{
  "id": "report_123",
  "status": "PENDING",
  "estimated_completion": "2024-01-15T10:05:00Z"
}
```

### Get Report Status

```http
GET /api/reports/{report_id}
```

**Response:**
```json
{
  "id": "report_123",
  "project_id": "proj_123",
  "report_type": "PROGRESS",
  "status": "COMPLETED",
  "format": "PDF",
  "file_url": "https://s3.amazonaws.com/buildpro/reports/report_123.pdf",
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:03:45Z"
}
```

**Status Values:**
- `PENDING` - Report generation queued
- `PROCESSING` - Currently generating
- `COMPLETED` - Ready for download
- `FAILED` - Generation failed

### List Reports

```http
GET /api/reports?project_id=proj_123
```

**Response:**
```json
{
  "items": [
    {
      "id": "report_123",
      "title": "Monthly Progress - January 2024",
      "report_type": "PROGRESS",
      "status": "COMPLETED",
      "created_at": "2024-01-31T10:00:00Z"
    }
  ]
}
```

---

## Files

### Get Presigned Upload URL

```http
POST /api/files/upload-url
```

**Request Body:**
```json
{
  "filename": "floor_plan.pdf",
  "content_type": "application/pdf",
  "file_size": 1024000
}
```

**Response:**
```json
{
  "upload_url": "https://s3.amazonaws.com/buildpro/...",
  "file_id": "file_123",
  "expires_in": 3600
}
```

**Usage:**
```javascript
// 1. Get upload URL
const { upload_url, file_id } = await api.post("/files/upload-url", {
  filename: file.name,
  content_type: file.type,
  file_size: file.size,
});

// 2. Upload file directly to S3
await fetch(upload_url, {
  method: "PUT",
  body: file,
  headers: { "Content-Type": file.type },
});

// 3. Save file metadata
await api.post("/files", {
  id: file_id,
  project_id: "proj_123",
  file_type: "DRAWING",
});
```

### Save File Metadata

```http
POST /api/files
```

**Request Body:**
```json
{
  "id": "file_123",
  "project_id": "proj_123",
  "filename": "floor_plan.pdf",
  "file_type": "DRAWING",
  "file_size": 1024000,
  "description": "Floor plan - Revision 3"
}
```

**Response:** `201 Created`

### Get Presigned Download URL

```http
GET /api/files/{file_id}/download-url
```

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/buildpro/...",
  "expires_in": 3600
}
```

### List Files

```http
GET /api/files?project_id=proj_123&file_type=DRAWING
```

**Response:**
```json
{
  "items": [
    {
      "id": "file_123",
      "filename": "floor_plan.pdf",
      "file_type": "DRAWING",
      "file_size": 1024000,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## Archive

### Search Archive

```http
GET /api/archive/search?status=COMPLETED&min_budget=1000000
```

**Query Parameters:**
- `status` (string, optional) - Project status
- `min_budget` (number, optional) - Minimum budget
- `max_budget` (number, optional) - Maximum budget
- `min_area` (number, optional) - Minimum home area (sqft)
- `max_area` (number, optional) - Maximum home area (sqft)
- `completed_after` (date, optional) - Completed after date (YYYY-MM-DD)
- `completed_before` (date, optional) - Completed before date

**Response:**
```json
{
  "items": [
    {
      "id": "proj_old_1",
      "title": "Lakeside Villas Phase 1",
      "status": "COMPLETED",
      "budget": 3200000.00,
      "actual_cost": 3050000.00,
      "variance": 150000.00,
      "home_area_sqft": 3200.00,
      "cost_per_sqft": 953.13,
      "lot_count": 24,
      "completed_date": "2023-12-15"
    }
  ]
}
```

### Compare Projects

```http
GET /api/archive/compare?project_ids=proj_1,proj_2,proj_3
```

**Response:**
```json
{
  "projects": [
    {
      "id": "proj_1",
      "title": "Lakeside Villas",
      "budget": 3200000.00,
      "actual_cost": 3050000.00,
      "variance": 150000.00,
      "cost_per_sqft": 953.13,
      "duration_days": 365
    }
  ],
  "averages": {
    "budget": 2900000.00,
    "cost_per_sqft": 920.00,
    "duration_days": 340
  }
}
```

---

## Data Models

### Enums

**ProjectStatus:**
- `PLANNING`
- `ACTIVE`
- `ON_HOLD`
- `COMPLETED`
- `CANCELLED`

**UserRole:**
- `OWNER` (6) - Full access
- `ADMIN` (5) - Manage users
- `PM` (4) - Manage projects
- `SUPERVISOR` (3) - Edit materials/schedule
- `ESTIMATOR` (2) - View/edit estimates
- `SUB` (1) - View only

**MaterialCategory:**
- `SITEWORK`, `FOUNDATION`, `CONCRETE`, `MASONRY`, `METALS`, `WOOD`, `FRAMING`, `THERMAL_MOISTURE`, `DOORS_WINDOWS`, `FINISHES`, `DRYWALL`, `FLOORING`, `PLUMBING`, `HVAC`, `ELECTRICAL`, `EQUIPMENT`, `FURNISHINGS`, `SPECIALTIES`, `OTHER`

**UnitOfMeasure:**
- `EA` (Each), `LF` (Linear Foot), `SF` (Square Foot), `SY` (Square Yard), `CY` (Cubic Yard), `CF` (Cubic Foot), `TON`, `LB` (Pound), `GAL` (Gallon), `LS` (Lump Sum), `HR` (Hour), `DAY`, `MO` (Month)

**MilestonePhase:**
- `SITEWORK`, `FOUNDATION`, `FRAMING`, `ROUGH_IN`, `DRYWALL`, `FINISHES`, `FINAL_INSPECTION`

**FileType:**
- `PDF`, `IMAGE`, `CSV`, `DRAWING`, `OTHER`

**ReportType:**
- `PROGRESS`, `BUDGET_VS_ACTUAL`, `TAKEOFF_SUMMARY`, `OM_BINDER`

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid auth token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Common Error Scenarios

**Missing Authorization:**
```json
{
  "detail": "Authorization header required",
  "status_code": 401
}
```

**Insufficient Permissions:**
```json
{
  "detail": "Insufficient permissions. Required role: ESTIMATOR",
  "status_code": 403
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "value must be greater than 0",
      "type": "value_error"
    }
  ],
  "status_code": 422
}
```

**Tenant Isolation:**
All endpoints automatically filter data by `tenant_id` from JWT. You cannot access data from other tenants.

---

## Rate Limiting

- **Default:** 100 requests per minute per tenant
- **Burst:** Up to 200 requests in 10 seconds
- Headers returned:
  - `X-RateLimit-Limit`: Requests allowed per window
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)

**Response:**
```json
{
  "items": [...],
  "total": 145,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

---

## Interactive API Documentation

Visit the interactive Swagger UI at:
- **Development:** http://localhost:8000/docs
- **Production:** https://api.buildpro.com/docs

---

**Last Updated:** January 2024
**API Version:** 1.0.0
