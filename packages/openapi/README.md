# OpenAPI Schema Artifacts

This package contains the OpenAPI schema generated from the FastAPI backend.

## Usage

The schema is automatically generated from the FastAPI application and can be accessed at:
- JSON: `http://localhost:8000/openapi.json`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Generating TypeScript Types

To generate TypeScript types from the OpenAPI schema:

```bash
# Install openapi-typescript
pnpm add -D openapi-typescript

# Generate types
npx openapi-typescript http://localhost:8000/openapi.json -o src/schema.d.ts
```

This allows the frontend to have type-safe API clients.
