"""
Product endpoint tests.
Covers: create, list, get one, update, patch, delete
Tests: success paths, RBAC enforcement, validation,
       pagination, search, filters, 404 handling
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.product import Product


# ══════════════════════════════════════════════════════════════════════════════
# CREATE PRODUCT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestCreateProduct:

    def test_create_product_as_admin_success(
        self,
        client: TestClient,
        admin_headers: dict,
        valid_product_payload: dict
    ):
        """Admin creates a product successfully."""
        response = client.post(
            "/api/v1/products",
            json=valid_product_payload,
            headers=admin_headers
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Product created successfully"
        assert body["data"]["name"] == valid_product_payload["name"]
        assert body["data"]["price"] == valid_product_payload["price"]
        assert body["data"]["stock"] == valid_product_payload["stock"]
        assert body["data"]["is_active"] is True
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    def test_create_product_as_user_forbidden(
        self,
        client: TestClient,
        user_headers: dict,
        valid_product_payload: dict
    ):
        """Regular user cannot create products — returns 403."""
        response = client.post(
            "/api/v1/products",
            json=valid_product_payload,
            headers=user_headers
        )

        assert response.status_code == 403
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "FORBIDDEN"

    def test_create_product_unauthenticated(
        self,
        client: TestClient,
        valid_product_payload: dict
    ):
        """Unauthenticated request to create product returns 401."""
        response = client.post("/api/v1/products", json=valid_product_payload)

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False

    def test_create_product_name_too_short(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product creation fails when name is under 2 characters."""
        response = client.post("/api/v1/products", json={
            "name": "A",
            "price": 99.99,
            "stock": 10
        }, headers=admin_headers)

        assert response.status_code == 422

    def test_create_product_price_zero(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product creation fails when price is zero."""
        response = client.post("/api/v1/products", json={
            "name": "Valid Product Name",
            "price": 0,
            "stock": 10
        }, headers=admin_headers)

        assert response.status_code == 422

    def test_create_product_negative_price(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product creation fails when price is negative."""
        response = client.post("/api/v1/products", json={
            "name": "Valid Product Name",
            "price": -10.00,
            "stock": 10
        }, headers=admin_headers)

        assert response.status_code == 422

    def test_create_product_negative_stock(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product creation fails when stock is negative."""
        response = client.post("/api/v1/products", json={
            "name": "Valid Product Name",
            "price": 99.99,
            "stock": -5
        }, headers=admin_headers)

        assert response.status_code == 422

    def test_create_product_zero_stock_allowed(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product with zero stock is valid — out of stock is allowed."""
        response = client.post("/api/v1/products", json={
            "name": "Out Of Stock Product",
            "price": 99.99,
            "stock": 0
        }, headers=admin_headers)

        assert response.status_code == 201
        assert response.json()["data"]["stock"] == 0

    def test_create_product_without_optional_fields(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product can be created without description and category."""
        response = client.post("/api/v1/products", json={
            "name": "Minimal Product",
            "price": 49.99,
            "stock": 5
        }, headers=admin_headers)

        assert response.status_code == 201
        body = response.json()
        assert body["data"]["description"] is None
        assert body["data"]["category"] is None

    def test_create_product_price_rounded_to_two_decimals(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product price is rounded to 2 decimal places."""
        response = client.post("/api/v1/products", json={
            "name": "Precision Price Product",
            "price": 99.999,
            "stock": 5
        }, headers=admin_headers)

        assert response.status_code == 201
        assert response.json()["data"]["price"] == 100.0

    def test_create_product_missing_required_fields(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product creation fails when required fields are missing."""
        response = client.post("/api/v1/products", json={
            "name": "Only Name"
        }, headers=admin_headers)

        assert response.status_code == 422

    def test_create_product_description_too_long(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Product creation fails when description exceeds 500 characters."""
        response = client.post("/api/v1/products", json={
            "name": "Valid Name",
            "description": "x" * 501,
            "price": 99.99,
            "stock": 10
        }, headers=admin_headers)

        assert response.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# LIST PRODUCTS TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestListProducts:

    def test_list_products_as_user_success(
        self,
        client: TestClient,
        user_headers: dict,
        multiple_products: list
    ):
        """Regular user can list products."""
        response = client.get("/api/v1/products", headers=user_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "pagination" in body
        assert isinstance(body["data"], list)

    def test_list_products_as_admin_success(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Admin can list products."""
        response = client.get("/api/v1/products", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

    def test_list_products_unauthenticated(
        self,
        client: TestClient,
        multiple_products: list
    ):
        """Unauthenticated request to list products returns 401."""
        response = client.get("/api/v1/products")

        assert response.status_code == 401

    def test_list_products_pagination_default(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Default pagination returns page 1 with 10 items."""
        response = client.get("/api/v1/products", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        pagination = body["pagination"]

        assert pagination["page"] == 1
        assert pagination["limit"] == 10
        assert "total" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_previous" in pagination
        assert pagination["has_previous"] is False

    def test_list_products_pagination_page_2(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Page 2 returns correct items and pagination metadata."""
        response = client.get(
            "/api/v1/products?page=2&limit=5",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["pagination"]["page"] == 2
        assert body["pagination"]["has_previous"] is True
        assert len(body["data"]) <= 5

    def test_list_products_search_by_name(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Search filters products by name."""
        response = client.get(
            "/api/v1/products?search=Test Product 1",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)

    def test_list_products_filter_by_category(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Category filter returns only matching products."""
        response = client.get(
            "/api/v1/products?category=Electronics",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        for product in body["data"]:
            assert "Electronics" in product["category"]

    def test_list_products_filter_min_price(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Min price filter returns only products at or above the price."""
        response = client.get(
            "/api/v1/products?min_price=50.00",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        for product in body["data"]:
            assert product["price"] >= 50.00

    def test_list_products_filter_max_price(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Max price filter returns only products at or below the price."""
        response = client.get(
            "/api/v1/products?max_price=100.00",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        for product in body["data"]:
            assert product["price"] <= 100.00

    def test_list_products_filter_in_stock(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """In-stock filter returns only products with stock > 0."""
        response = client.get(
            "/api/v1/products?in_stock=true",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        for product in body["data"]:
            assert product["stock"] > 0

    def test_list_products_empty_search_returns_all(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Empty search term returns all products."""
        response = client.get("/api/v1/products", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["pagination"]["total"] >= len(multiple_products)

    def test_list_products_limit_respected(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Limit parameter is respected in response."""
        response = client.get(
            "/api/v1/products?limit=3",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) <= 3
        assert body["pagination"]["limit"] == 3

    def test_list_products_pagination_structure(
        self,
        client: TestClient,
        admin_headers: dict,
        multiple_products: list
    ):
        """Pagination object has all required fields."""
        response = client.get("/api/v1/products", headers=admin_headers)

        assert response.status_code == 200
        pagination = response.json()["pagination"]

        required_fields = [
            "total", "page", "limit",
            "total_pages", "has_next", "has_previous"
        ]
        for field in required_fields:
            assert field in pagination, f"Missing pagination field: {field}"


# ══════════════════════════════════════════════════════════════════════════════
# GET SINGLE PRODUCT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestGetProduct:

    def test_get_product_as_user_success(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """Regular user can get a single product by ID."""
        response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=user_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == test_product.id
        assert body["data"]["name"] == test_product.name
        assert body["data"]["price"] == test_product.price

    def test_get_product_as_admin_success(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Admin can get a single product by ID."""
        response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        assert response.json()["data"]["id"] == test_product.id

    def test_get_product_not_found(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Returns 404 for non-existent product ID."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/products/{fake_id}",
            headers=admin_headers
        )

        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "NOT_FOUND"

    def test_get_product_unauthenticated(
        self,
        client: TestClient,
        test_product: Product
    ):
        """Unauthenticated request returns 401."""
        response = client.get(f"/api/v1/products/{test_product.id}")

        assert response.status_code == 401

    def test_get_product_response_has_required_fields(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Product response contains all required fields."""
        response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]

        required_fields = [
            "id", "name", "description", "price",
            "stock", "category", "is_active",
            "created_by", "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE PRODUCT (PUT) TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestUpdateProduct:

    def test_full_update_as_admin_success(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Admin can fully update a product."""
        update_payload = {
            "name": "Updated Product Name",
            "description": "Updated description text",
            "price": 399.99,
            "stock": 100,
            "category": "Updated Category"
        }

        response = client.put(
            f"/api/v1/products/{test_product.id}",
            json=update_payload,
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["name"] == "Updated Product Name"
        assert body["data"]["price"] == 399.99
        assert body["data"]["stock"] == 100

    def test_full_update_as_user_forbidden(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """Regular user cannot update products — returns 403."""
        response = client.put(
            f"/api/v1/products/{test_product.id}",
            json={
                "name": "Hacked Name",
                "price": 1.00,
                "stock": 999
            },
            headers=user_headers
        )

        assert response.status_code == 403
        body = response.json()
        assert body["error_code"] == "FORBIDDEN"

    def test_full_update_unauthenticated(
        self,
        client: TestClient,
        test_product: Product
    ):
        """Unauthenticated update request returns 401."""
        response = client.put(
            f"/api/v1/products/{test_product.id}",
            json={"name": "Test", "price": 10.00, "stock": 5}
        )

        assert response.status_code == 401

    def test_full_update_product_not_found(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Full update returns 404 for non-existent product."""
        response = client.put(
            f"/api/v1/products/{uuid.uuid4()}",
            json={
                "name": "Doesnt Matter",
                "price": 10.00,
                "stock": 5
            },
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_full_update_invalid_price(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Full update fails with invalid price."""
        response = client.put(
            f"/api/v1/products/{test_product.id}",
            json={
                "name": "Valid Name",
                "price": -50.00,
                "stock": 10
            },
            headers=admin_headers
        )

        assert response.status_code == 422

    def test_full_update_persists_changes(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Updated values are actually persisted and returned on next GET."""
        new_name = "Persistently Updated Name"

        client.put(
            f"/api/v1/products/{test_product.id}",
            json={
                "name": new_name,
                "price": 150.00,
                "stock": 30
            },
            headers=admin_headers
        )

        get_response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )

        assert get_response.status_code == 200
        assert get_response.json()["data"]["name"] == new_name


# ══════════════════════════════════════════════════════════════════════════════
# PATCH PRODUCT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestPatchProduct:

    def test_patch_price_only_as_admin(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Admin can patch only the price field."""
        original_name = test_product.name

        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"price": 149.99},
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["price"] == 149.99
        # Name should remain unchanged
        assert body["data"]["name"] == original_name

    def test_patch_stock_only_as_admin(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Admin can patch only the stock field."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"stock": 999},
            headers=admin_headers
        )

        assert response.status_code == 200
        assert response.json()["data"]["stock"] == 999

    def test_patch_multiple_fields(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Admin can patch multiple fields at once."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"price": 249.99, "stock": 50, "category": "New Category"},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["price"] == 249.99
        assert data["stock"] == 50
        assert data["category"] == "New Category"

    def test_patch_as_user_forbidden(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """Regular user cannot patch products."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"price": 1.00},
            headers=user_headers
        )

        assert response.status_code == 403

    def test_patch_unauthenticated(
        self,
        client: TestClient,
        test_product: Product
    ):
        """Unauthenticated patch request returns 401."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"price": 1.00}
        )

        assert response.status_code == 401

    def test_patch_empty_body_returns_400(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Patch with empty body returns 400 bad request."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={},
            headers=admin_headers
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "BAD_REQUEST"

    def test_patch_not_found(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Patch returns 404 for non-existent product."""
        response = client.patch(
            f"/api/v1/products/{uuid.uuid4()}",
            json={"price": 50.00},
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_patch_invalid_price(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Patch fails with invalid price value."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"price": 0},
            headers=admin_headers
        )

        assert response.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# DELETE PRODUCT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestDeleteProduct:

    def test_delete_product_as_admin_success(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Admin can delete a product successfully."""
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "deleted" in body["message"].lower()

    def test_delete_product_as_user_forbidden(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """Regular user cannot delete products — returns 403."""
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=user_headers
        )

        assert response.status_code == 403
        body = response.json()
        assert body["error_code"] == "FORBIDDEN"

    def test_delete_product_unauthenticated(
        self,
        client: TestClient,
        test_product: Product
    ):
        """Unauthenticated delete request returns 401."""
        response = client.delete(f"/api/v1/products/{test_product.id}")

        assert response.status_code == 401

    def test_delete_product_not_found(
        self,
        client: TestClient,
        admin_headers: dict
    ):
        """Delete returns 404 for non-existent product."""
        response = client.delete(
            f"/api/v1/products/{uuid.uuid4()}",
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_delete_is_soft_delete(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Deleted product returns 404 on subsequent GET — soft delete works."""
        # Delete the product
        delete_response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )
        assert delete_response.status_code == 200

        # Try to get it — should return 404 since is_active = False
        get_response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )
        assert get_response.status_code == 404

    def test_delete_product_disappears_from_list(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Deleted product no longer appears in product list."""
        product_id = test_product.id

        # Delete
        client.delete(
            f"/api/v1/products/{product_id}",
            headers=admin_headers
        )

        # List and check it is gone
        list_response = client.get("/api/v1/products", headers=admin_headers)
        product_ids = [p["id"] for p in list_response.json()["data"]]
        assert product_id not in product_ids

    def test_delete_already_deleted_product(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """Deleting an already-deleted product returns 404."""
        # First delete
        client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )

        # Second delete — should 404
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=admin_headers
        )
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# RBAC COMPREHENSIVE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestRBAC:
    """
    Dedicated RBAC tests that explicitly verify the role boundary.
    These are the most important tests from an evaluation perspective.
    """

    def test_user_cannot_create_product(
        self,
        client: TestClient,
        user_headers: dict
    ):
        """RBAC: user role blocked from POST /products."""
        response = client.post(
            "/api/v1/products",
            json={"name": "Test", "price": 10.00, "stock": 1},
            headers=user_headers
        )
        assert response.status_code == 403

    def test_user_cannot_update_product(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """RBAC: user role blocked from PUT /products/{id}."""
        response = client.put(
            f"/api/v1/products/{test_product.id}",
            json={"name": "Test", "price": 10.00, "stock": 1},
            headers=user_headers
        )
        assert response.status_code == 403

    def test_user_cannot_patch_product(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """RBAC: user role blocked from PATCH /products/{id}."""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"price": 1.00},
            headers=user_headers
        )
        assert response.status_code == 403

    def test_user_cannot_delete_product(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """RBAC: user role blocked from DELETE /products/{id}."""
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=user_headers
        )
        assert response.status_code == 403

    def test_admin_can_access_all_endpoints(
        self,
        client: TestClient,
        admin_headers: dict,
        test_product: Product
    ):
        """RBAC: admin role has access to all product endpoints."""
        # GET list
        r1 = client.get("/api/v1/products", headers=admin_headers)
        assert r1.status_code == 200

        # GET one
        r2 = client.get(f"/api/v1/products/{test_product.id}", headers=admin_headers)
        assert r2.status_code == 200

        # POST
        r3 = client.post("/api/v1/products", json={
            "name": "Admin Test Product",
            "price": 99.99,
            "stock": 10
        }, headers=admin_headers)
        assert r3.status_code == 201

        # PATCH
        r4 = client.patch(
            f"/api/v1/products/{test_product.id}",
            json={"stock": 5},
            headers=admin_headers
        )
        assert r4.status_code == 200

    def test_user_can_read_products(
        self,
        client: TestClient,
        user_headers: dict,
        test_product: Product
    ):
        """RBAC: user role has read access to products."""
        r1 = client.get("/api/v1/products", headers=user_headers)
        assert r1.status_code == 200

        r2 = client.get(f"/api/v1/products/{test_product.id}", headers=user_headers)
        assert r2.status_code == 200

    def test_expired_token_returns_401(self, client: TestClient):
        """Expired or tampered JWT returns 401 on protected endpoints."""
        fake_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.fakesignature"
        response = client.get(
            "/api/v1/products",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        assert response.status_code == 401