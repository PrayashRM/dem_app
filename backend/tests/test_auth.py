"""
Auth endpoint tests.
Covers: register, login, /me
Tests: success paths, validation, duplicates, wrong credentials,
       JWT protection, inactive accounts
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


# ══════════════════════════════════════════════════════════════════════════════
# REGISTER TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestRegister:

    def test_register_success(self, client: TestClient, valid_register_payload: dict):
        """New user registers successfully with valid data."""
        response = client.post("/api/v1/auth/register", json=valid_register_payload)

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Account created successfully"
        assert "data" in body
        assert body["data"]["email"] == valid_register_payload["email"]
        assert body["data"]["role"] == "user"
        assert body["data"]["is_active"] is True
        # Password must never appear in response
        assert "password" not in body["data"]
        assert "hashed_password" not in body["data"]

    def test_register_duplicate_email(
        self,
        client: TestClient,
        test_regular_user: User,
        valid_register_payload: dict
    ):
        """Registration fails when email already exists."""
        valid_register_payload["email"] = test_regular_user.email

        response = client.post("/api/v1/auth/register", json=valid_register_payload)

        assert response.status_code == 409
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "CONFLICT"

    def test_register_invalid_email_format(self, client: TestClient):
        """Registration fails with malformed email."""
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "full_name": "Test User",
            "password": "ValidPass123"
        })

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "VALIDATION_ERROR"

    def test_register_password_too_short(self, client: TestClient):
        """Registration fails when password is under 8 characters."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "Test User",
            "password": "Ab1"
        })

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False

    def test_register_password_no_uppercase(self, client: TestClient):
        """Registration fails when password has no uppercase letter."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "Test User",
            "password": "nouppercase1"
        })

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "VALIDATION_ERROR"

    def test_register_password_no_digit(self, client: TestClient):
        """Registration fails when password has no digit."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "Test User",
            "password": "NoDigitHere"
        })

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False

    def test_register_password_no_lowercase(self, client: TestClient):
        """Registration fails when password has no lowercase letter."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "Test User",
            "password": "NOLOWER123"
        })

        assert response.status_code == 422

    def test_register_full_name_too_short(self, client: TestClient):
        """Registration fails when full name is under 2 characters."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "A",
            "password": "ValidPass123"
        })

        assert response.status_code == 422

    def test_register_full_name_with_numbers(self, client: TestClient):
        """Registration fails when full name contains non-alphabetic characters."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "full_name": "John123",
            "password": "ValidPass123"
        })

        assert response.status_code == 422

    def test_register_missing_required_fields(self, client: TestClient):
        """Registration fails when required fields are missing."""
        response = client.post("/api/v1/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com"
        })

        assert response.status_code == 422

    def test_register_empty_body(self, client: TestClient):
        """Registration fails with empty request body."""
        response = client.post("/api/v1/auth/register", json={})

        assert response.status_code == 422

    def test_register_new_user_gets_user_role(
        self,
        client: TestClient,
        valid_register_payload: dict
    ):
        """Newly registered user always gets role=user, never admin."""
        response = client.post("/api/v1/auth/register", json=valid_register_payload)

        assert response.status_code == 201
        assert response.json()["data"]["role"] == "user"

    def test_register_email_case_insensitive(
        self,
        client: TestClient,
        test_regular_user: User
    ):
        """Registration rejects uppercase version of existing email."""
        response = client.post("/api/v1/auth/register", json={
            "email": test_regular_user.email.upper(),
            "full_name": "Test User",
            "password": "ValidPass123"
        })

        assert response.status_code == 409


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestLogin:

    def test_login_success_regular_user(
        self,
        client: TestClient,
        test_regular_user: User
    ):
        """Regular user logs in successfully and receives JWT."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_regular_user.email,
            "password": "UserPass123"
        })

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Login successful"
        assert "access_token" in body["data"]
        assert body["data"]["token_type"] == "bearer"
        assert body["data"]["expires_in"] > 0
        assert body["data"]["user"]["email"] == test_regular_user.email
        assert body["data"]["user"]["role"] == "user"

    def test_login_success_admin_user(
        self,
        client: TestClient,
        test_admin_user: User
    ):
        """Admin user logs in successfully and JWT contains admin role."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_admin_user.email,
            "password": "AdminPass123"
        })

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["user"]["role"] == "admin"
        assert "access_token" in body["data"]

    def test_login_wrong_password(
        self,
        client: TestClient,
        test_regular_user: User
    ):
        """Login fails with correct email but wrong password."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_regular_user.email,
            "password": "WrongPassword999"
        })

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "UNAUTHORIZED"

    def test_login_wrong_email(self, client: TestClient):
        """Login fails with non-existent email."""
        response = client.post("/api/v1/auth/login", json={
            "email": "doesnotexist@nowhere.com",
            "password": "SomePass123"
        })

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False

    def test_login_inactive_user(
        self,
        client: TestClient,
        test_inactive_user: User
    ):
        """Login fails for deactivated user accounts."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_inactive_user.email,
            "password": "InactivePass123"
        })

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False

    def test_login_invalid_email_format(self, client: TestClient):
        """Login fails with invalid email format."""
        response = client.post("/api/v1/auth/login", json={
            "email": "not-valid-email",
            "password": "SomePass123"
        })

        assert response.status_code == 422

    def test_login_missing_password(self, client: TestClient):
        """Login fails when password field is missing."""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@test.com"
        })

        assert response.status_code == 422

    def test_login_missing_email(self, client: TestClient):
        """Login fails when email field is missing."""
        response = client.post("/api/v1/auth/login", json={
            "password": "SomePass123"
        })

        assert response.status_code == 422

    def test_login_empty_body(self, client: TestClient):
        """Login fails with empty request body."""
        response = client.post("/api/v1/auth/login", json={})

        assert response.status_code == 422

    def test_login_returns_token_structure(
        self,
        client: TestClient,
        test_regular_user: User
    ):
        """Login response has all required token fields."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_regular_user.email,
            "password": "UserPass123"
        })

        assert response.status_code == 200
        data = response.json()["data"]

        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 20

    def test_login_does_not_expose_password(
        self,
        client: TestClient,
        test_regular_user: User
    ):
        """Login response never contains password or hashed_password."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_regular_user.email,
            "password": "UserPass123"
        })

        response_text = response.text
        assert "hashed_password" not in response_text
        assert "UserPass123" not in response_text


# ══════════════════════════════════════════════════════════════════════════════
# GET /ME TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestGetMe:

    def test_get_me_success_regular_user(
        self,
        client: TestClient,
        test_regular_user: User,
        user_headers: dict
    ):
        """Authenticated user gets their own profile."""
        response = client.get("/api/v1/auth/me", headers=user_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["email"] == test_regular_user.email
        assert body["data"]["role"] == "user"
        assert body["data"]["is_active"] is True

    def test_get_me_success_admin_user(
        self,
        client: TestClient,
        test_admin_user: User,
        admin_headers: dict
    ):
        """Authenticated admin gets their own profile with admin role."""
        response = client.get("/api/v1/auth/me", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["role"] == "admin"

    def test_get_me_no_token(self, client: TestClient):
        """Unauthenticated request to /me returns 401."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False

    def test_get_me_invalid_token(self, client: TestClient):
        """Invalid JWT token returns 401."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer completely.invalid.token"}
        )

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False

    def test_get_me_malformed_auth_header(self, client: TestClient):
        """Malformed Authorization header returns 401."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "NotBearer sometoken"}
        )

        assert response.status_code == 401

    def test_get_me_does_not_expose_password(
        self,
        client: TestClient,
        user_headers: dict
    ):
        """Profile response never contains hashed password."""
        response = client.get("/api/v1/auth/me", headers=user_headers)

        response_text = response.text
        assert "hashed_password" not in response_text

    def test_get_me_response_has_required_fields(
        self,
        client: TestClient,
        user_headers: dict
    ):
        """Profile response contains all required user fields."""
        response = client.get("/api/v1/auth/me", headers=user_headers)

        assert response.status_code == 200
        data = response.json()["data"]

        required_fields = ["id", "email", "full_name", "role", "is_active", "created_at"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"