import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api.v1 import api_v1_router
from app.utils.exceptions import AppException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("Application shutting down")


# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Product Management System API

A secure, scalable REST API with JWT authentication and Role-Based Access Control.

### Features
- **JWT Authentication** — Secure token-based auth
- **Role-Based Access** — User and Admin roles
- **Product CRUD** — Full product management
- **Pagination & Search** — Scalable data retrieval
- **Input Validation** — Pydantic-powered validation
- **Soft Deletes** — Data integrity preservation

### Authentication
Use the `/api/v1/auth/login` endpoint to get a JWT token.
Click **Authorize** and enter: `Bearer <your_token>`

### Default Admin Credentials
- **Email:** admin@example.com
- **Password:** Admin123
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)


# ── Exception Handlers ─────────────────────────────────────────────────────────

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle all custom application exceptions."""
    logger.warning(
        f"AppException [{exc.status_code}] on {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": getattr(exc, "error_code", "ERROR")
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard HTTP exceptions."""
    logger.warning(
        f"HTTPException [{exc.status_code}] on {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": "HTTP_ERROR"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    Returns clean, readable error messages instead of raw Pydantic output.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"].replace("Value error, ", ""),
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.method} {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed. Please check your input.",
            "error_code": "VALIDATION_ERROR",
            "details": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle unexpected database errors."""
    logger.error(
        f"Database error on {request.method} {request.url.path}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "A database error occurred. Please try again.",
            "error_code": "DATABASE_ERROR"
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exceptions."""
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# ── Routers ────────────────────────────────────────────────────────────────────

app.include_router(api_v1_router)


# ── Health Check ───────────────────────────────────────────────────────────────

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API server is running."
)
def health_check():
    """Basic health check endpoint."""
    return {
        "success": True,
        "message": "Server is running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get(
    "/",
    tags=["Health"],
    summary="Root",
    include_in_schema=False
)
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }