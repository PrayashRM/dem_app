"""
Shared test fixtures and configuration.
Uses SQLite in-memory database for speed and full isolation.
Each test function gets a clean rolled-back transaction.
"""

import pytest
import uuid
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, String, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# ── Import Base and models BEFORE creating test engine ────────────────────────
from app.database.db import Base, get_db
from app.core.security import hash_password, create_access_token


# ── Test Database ─────────────────────────────────────────────────────────────
# SQLite in-memory with StaticPool so the same connection
# is reused across the entire test session

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# ── SQLite ENUM fix ───────────────────────────────────────────────────────────
# PostgreSQL ENUM types do not exist in SQLite.
# We override the column type at the engine level using a listen event
# so SQLite treats the role column as a plain VARCHAR.
# This does NOT affect the production PostgreSQL setup at all.

from sqlalchemy import event as sa_event
from sqlalchemy.engine import Engine
import sqlite3

@sa_event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key support in SQLite for tests."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ── Patch ENUM for SQLite ─────────────────────────────────────────────────────
# Replace the PostgreSQL ENUM with plain String on the User model
# so SQLite can create the table without errors.
# Must be done BEFORE create_all is called.

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from app.models.user import User
from app.models.product import Product

# Find the role column and replace its type with String for SQLite
_role_col = User.__table__.c.get("role")
if _role_col is not None and isinstance(_role_col.type, PG_ENUM):
    _role_col.type = String(20)


# ── Create Tables Once ────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """
    Creates all tables once for the entire test session.
    Drops everything first to guarantee a clean slate.
    """
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ── DB Session Fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Provides a clean DB session per test.
    Uses a savepoint so each test rolls back all its changes.
    Keeps tests fully isolated from each other.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ── Test Client Fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Provides a FastAPI TestClient with the test DB injected.
    Overrides get_db so all API requests hit the test database.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    from app.main import app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


# ── User Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def test_admin_user(db: Session) -> User:
    """Fresh admin user for each test."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        full_name="Test Admin",
        hashed_password=hash_password("AdminPass123"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_regular_user(db: Session) -> User:
    """Fresh regular user for each test."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"user_{uuid.uuid4().hex[:8]}@test.com",
        full_name="Test User",
        hashed_password=hash_password("UserPass123"),
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_inactive_user(db: Session) -> User:
    """Deactivated user for testing blocked access."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"inactive_{uuid.uuid4().hex[:8]}@test.com",
        full_name="Inactive User",
        hashed_password=hash_password("InactivePass123"),
        role="user",
        is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Token Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def admin_token(test_admin_user: User) -> str:
    """Valid JWT for admin user."""
    return create_access_token(
        subject=test_admin_user.id,
        role="admin"
    )


@pytest.fixture(scope="function")
def user_token(test_regular_user: User) -> str:
    """Valid JWT for regular user."""
    return create_access_token(
        subject=test_regular_user.id,
        role="user"
    )


@pytest.fixture(scope="function")
def admin_headers(admin_token: str) -> dict:
    """Auth headers for admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def user_headers(user_token: str) -> dict:
    """Auth headers for regular user requests."""
    return {"Authorization": f"Bearer {user_token}"}


# ── Product Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def test_product(db: Session, test_admin_user: User) -> Product:
    """Single sample product for each test."""
    product = Product(
        id=str(uuid.uuid4()),
        name="Test Wireless Headphones",
        description="High quality wireless headphones for testing",
        price=199.99,
        stock=25,
        category="Electronics",
        is_active=True,
        created_by=test_admin_user.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture(scope="function")
def multiple_products(db: Session, test_admin_user: User) -> list:
    """15 sample products for pagination and filter testing."""
    products = []
    categories = ["Electronics", "Furniture", "Accessories"]

    for i in range(1, 16):
        product = Product(
            id=str(uuid.uuid4()),
            name=f"Test Product {i}",
            description=f"Description for test product {i}",
            price=round(10.00 * i, 2),
            stock=i * 5,
            category=categories[i % 3],
            is_active=True,
            created_by=test_admin_user.id
        )
        db.add(product)
        products.append(product)

    db.commit()
    for p in products:
        db.refresh(p)
    return products


# ── Payload Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def valid_register_payload() -> dict:
    """Valid registration payload with unique email."""
    return {
        "email": f"newuser_{uuid.uuid4().hex[:8]}@test.com",
        "full_name": "New Test User",
        "password": "ValidPass123"
    }


@pytest.fixture
def valid_product_payload() -> dict:
    """Valid product creation payload."""
    return {
        "name": "New Test Product",
        "description": "A product created during testing",
        "price": 99.99,
        "stock": 10,
        "category": "Electronics"
    }