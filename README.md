# Product Management System

A secure, production-structured REST API built with **FastAPI**, **PostgreSQL**,
and **JWT authentication**, featuring Role-Based Access Control (RBAC),
API versioning, Swagger documentation, and a lightweight React frontend.

---

## Tech Stack

| Layer       | Technology                              |
|-------------|----------------------------------------|
| Backend     | FastAPI, Python 3.11                   |
| Database    | PostgreSQL 15, SQLAlchemy 2, Alembic   |
| Auth        | JWT (python-jose), bcrypt (passlib)    |
| Validation  | Pydantic v2                            |
| Frontend    | React 18, Vite, Axios                  |
| DevOps      | Docker, Docker Compose                 |
| Docs        | Swagger UI, ReDoc                      |

---

## Project Structure

```
product-management-system/
│
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (auth, products)
│   │   ├── core/            # Config, JWT, security
│   │   ├── database/        # SQLAlchemy engine and session
│   │   ├── dependencies/    # FastAPI reusable dependencies
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── utils/           # Exceptions, response formatters
│   │   └── main.py          # App entry point
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Seed script
│   ├── tests/               # Pytest test suite
│   ├── docker/              # PgAdmin config
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   └── requirements.txt
│
└── frontend/
    └── src/                 # React + Vite frontend
```

---

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git

### 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/product-management-system.git
cd product-management-system/backend
```

### 2 — Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```bash
# Minimum required changes
SECRET_KEY=your-super-secret-key-min-32-characters-long
POSTGRES_PASSWORD=your-secure-db-password
DATABASE_URL=postgresql://postgres:your-secure-db-password@db:5432/product_management_db
```

Generate a strong secret key:

```bash
openssl rand -hex 32
```

### 3 — Start All Services

```bash
docker compose up --build
```

This single command:
- Starts PostgreSQL database
- Starts PgAdmin dashboard
- Builds and starts the FastAPI backend
- Runs database migrations automatically
- Seeds default admin and user accounts automatically

### 4 — Verify Everything is Running

```
FastAPI Backend  → http://localhost:8000
Swagger Docs     → http://localhost:8000/docs
ReDoc            → http://localhost:8000/redoc
Health Check     → http://localhost:8000/health
PgAdmin          → http://localhost:5050
```

---

## Default Credentials

### API Accounts

| Role  | Email               | Password  |
|-------|---------------------|-----------|
| Admin | admin@example.com   | Admin123  |
| User  | user@example.com    | User1234  |

### PgAdmin

| Field    | Value                  |
|----------|------------------------|
| Email    | admin@pgadmin.com      |
| Password | pgadminpassword        |
| URL      | http://localhost:5050  |

> PgAdmin auto-connects to PostgreSQL. No manual server setup needed.

---

## API Reference

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

All protected endpoints require a Bearer token in the header:

```
Authorization: Bearer <your_jwt_token>
```

Get your token from `POST /api/v1/auth/login`.

---

### Auth Endpoints

| Method | Endpoint              | Access | Description              |
|--------|-----------------------|--------|--------------------------|
| POST   | /api/v1/auth/register | Public | Create new user account  |
| POST   | /api/v1/auth/login    | Public | Login and get JWT token  |
| GET    | /api/v1/auth/me       | Any    | Get current user profile |

---

### Product Endpoints

| Method | Endpoint                  | Access | Description                   |
|--------|---------------------------|--------|-------------------------------|
| POST   | /api/v1/products          | Admin  | Create a product              |
| GET    | /api/v1/products          | Any    | List products with pagination |
| GET    | /api/v1/products/{id}     | Any    | Get single product            |
| PUT    | /api/v1/products/{id}     | Admin  | Full update a product         |
| PATCH  | /api/v1/products/{id}     | Admin  | Partial update a product      |
| DELETE | /api/v1/products/{id}     | Admin  | Soft delete a product         |

---

### Query Parameters for GET /api/v1/products

| Parameter  | Type    | Default | Description                    |
|------------|---------|---------|--------------------------------|
| page       | integer | 1       | Page number                    |
| limit      | integer | 10      | Items per page (max 100)       |
| search     | string  | —       | Search in name and description |
| category   | string  | —       | Filter by category             |
| min_price  | float   | —       | Minimum price filter           |
| max_price  | float   | —       | Maximum price filter           |
| in_stock   | boolean | —       | Filter by stock availability   |

---

### Response Format

Every response follows this consistent envelope:

**Success**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

**Paginated**
```json
{
  "success": true,
  "message": "Products retrieved successfully",
  "data": [],
  "pagination": {
    "total": 50,
    "page": 1,
    "limit": 10,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

**Error**
```json
{
  "success": false,
  "message": "Resource not found",
  "error_code": "NOT_FOUND"
}
```

**Validation Error**
```json
{
  "success": false,
  "message": "Validation failed. Please check your input.",
  "error_code": "VALIDATION_ERROR",
  "details": [
    {
      "field": "password",
      "message": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```

---

## Testing the API with Swagger

1. Open `http://localhost:8000/docs`
2. Use `POST /api/v1/auth/login` with admin credentials
3. Copy the `access_token` from the response
4. Click the **Authorize** button at the top right of Swagger
5. Enter `Bearer <your_token>`
6. All protected endpoints are now unlocked

---

## Running Tests

```bash
# Run all tests
docker compose exec api pytest tests/ -v

# Run with coverage report
docker compose exec api pytest tests/ -v --tb=short

# Run only auth tests
docker compose exec api pytest tests/test_auth.py -v

# Run only product tests
docker compose exec api pytest tests/test_products.py -v
```

---

## Database Management

### Run Migrations Manually

```bash
docker compose exec api alembic upgrade head
```

### Create a New Migration After Model Changes

```bash
docker compose exec api alembic revision --autogenerate -m "describe your change"
```

### Check Migration Status

```bash
docker compose exec api alembic current
docker compose exec api alembic history --verbose
```

### Rollback One Migration

```bash
docker compose exec api alembic downgrade -1
```

### Re-run Seed Script

```bash
docker compose exec api python scripts/seed.py
```

---

## Useful Docker Commands

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up --build -d

# View live API logs
docker compose logs -f api

# View all logs
docker compose logs -f

# Rebuild only the API container
docker compose up --build api

# Stop all containers
docker compose down

# Stop and delete all data volumes (full reset)
docker compose down -v

# Open shell inside API container
docker compose exec api sh

# Connect to PostgreSQL directly
docker exec -it pms_postgres psql -U postgres -d product_management_db
```

---

## Security Design

### JWT Authentication
- Tokens are signed with HS256 algorithm using a secret key
- Token expiry is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- Token payload contains user ID and role
- Tokens are stateless — no server-side session storage

### Password Security
- All passwords hashed with bcrypt via passlib
- Raw passwords are never stored or logged anywhere
- Login uses constant-time comparison to prevent timing attacks

### Role-Based Access Control
- Two roles: `user` and `admin`
- Role is embedded in JWT at login time
- Every protected endpoint independently verifies role from token
- No user can self-promote to admin via the API
- Admin accounts are created only via seed script or direct DB update

### Input Validation
- All inputs validated by Pydantic v2 before hitting business logic
- Validation errors return structured field-level messages
- SQL injection is prevented by SQLAlchemy ORM parameterized queries

### Soft Deletes
- Products are never permanently deleted
- `is_active = false` marks a product as deleted
- Preserves audit trail and referential integrity

---

## Admin Management via Database

Promote a user to admin:
```sql
UPDATE users SET role = 'admin' WHERE email = 'someone@example.com';
```

Deactivate a user account:
```sql
UPDATE users SET is_active = false WHERE email = 'someone@example.com';
```

Reactivate a user account:
```sql
UPDATE users SET is_active = true WHERE email = 'someone@example.com';
```

---

## Scalability Considerations

### Current Architecture
The system is designed stateless from day one, which means it can scale
horizontally without any architectural changes.

### Horizontal Scaling
- FastAPI is stateless — multiple instances can run behind a load balancer
- JWT tokens require no shared session state between instances
- PostgreSQL connection pooling (QueuePool) is already configured
- Docker-ready structure allows immediate deployment to any container
  orchestration platform (ECS, Kubernetes)

### Caching Layer (Redis — Next Step)
- Product listings are ideal candidates for Redis caching
- Cache invalidation on create, update, delete operations
- Would reduce DB read load significantly under high traffic
- Can be added as a new Docker service without touching existing code

### Database Scaling
- Read replicas can be added for GET endpoints to distribute load
- Alembic migrations make schema changes safe and trackable
  across all environments
- Composite indexes are already in place for common query patterns
  (name + category, is_active + created_at, is_active + price)
- Soft deletes preserve data integrity without blocking queries

### Modular Service Layer
- Business logic is fully separated from route handlers
- Each service (auth_service, product_service) can be extracted
  into an independent microservice with minimal changes
- New entities (orders, reviews, inventory) can be added as new
  modules without touching existing code

### API Versioning
- All routes are prefixed with `/api/v1`
- Breaking changes ship under `/api/v2` without affecting existing clients
- Both versions can run simultaneously during transition periods

### Logging and Observability
- Structured logging is in place across all layers
- Log level is controlled by `DEBUG` environment variable
- Ready for integration with centralized logging (CloudWatch, Datadog)

### Deployment Path
```
Current  → Docker Compose (single server)
Next     → AWS ECS or EC2 with RDS PostgreSQL
Scale    → ECS with Auto Scaling + ElastiCache Redis + RDS Read Replicas
Advanced → Microservices per domain with API Gateway
```

---

## Environment Variables Reference

| Variable                  | Required | Default                    | Description                     |
|---------------------------|----------|----------------------------|---------------------------------|
| DATABASE_URL              | Yes      | —                          | Full PostgreSQL connection URL  |
| SECRET_KEY                | Yes      | —                          | JWT signing secret (min 32 chars)|
| ALGORITHM                 | No       | HS256                      | JWT algorithm                   |
| ACCESS_TOKEN_EXPIRE_MINUTES| No      | 30                         | Token expiry in minutes         |
| APP_NAME                  | No       | Product Management System  | Application name                |
| APP_VERSION               | No       | 1.0.0                      | Application version             |
| DEBUG                     | No       | False                      | Enable SQL query logging        |
| ALLOWED_ORIGINS           | No       | localhost:5173, 3000       | CORS allowed origins            |
| POSTGRES_USER             | Yes      | —                          | PostgreSQL username             |
| POSTGRES_PASSWORD         | Yes      | —                          | PostgreSQL password             |
| POSTGRES_DB               | Yes      | —                          | PostgreSQL database name        |
| PGADMIN_DEFAULT_EMAIL     | Yes      | —                          | PgAdmin login email             |
| PGADMIN_DEFAULT_PASSWORD  | Yes      | —                          | PgAdmin login password          |

---

## License

MIT License. Free to use for educational and professional purposes.