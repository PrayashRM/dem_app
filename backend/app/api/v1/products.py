from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.db import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductPatch, ProductResponse
)
from app.services.product_service import (
    create_product, get_products, get_product_by_id,
    update_product, patch_product, delete_product
)
from app.dependencies.auth import get_current_active_user, require_admin
from app.utils.responses import success_response, paginated_response
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
    description="Admin only. Create a new product in the catalog."
)
def create(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new product. **Admin only.**

    - **name**: 2–100 characters
    - **price**: Must be greater than 0
    - **stock**: Must be 0 or greater
    - **category**: Optional product category
    """
    product = create_product(db, payload, current_user)
    return success_response(
        data=ProductResponse.model_validate(product).model_dump(mode="json"),
        message="Product created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List products",
    description="Get paginated list of products with optional search and filters."
)
def list_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search in name and description"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    min_price: Optional[float] = Query(default=None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(default=None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(default=None, description="Filter by stock availability"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paginated product list. Available to all authenticated users.

    Supports filtering by search term, category, price range, and stock status.
    """
    result = get_products(
        db=db,
        page=page,
        limit=limit,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock
    )

    serialized_items = [
        ProductResponse.model_validate(item).model_dump(mode="json")
        for item in result["items"]
    ]

    return paginated_response(
        items=serialized_items,
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        message="Products retrieved successfully"
    )


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a product",
    description="Get a single product by its ID."
)
def get_one(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single product by ID. Available to all authenticated users.
    """
    product = get_product_by_id(db, product_id)
    return success_response(
        data=ProductResponse.model_validate(product).model_dump(mode="json"),
        message="Product retrieved successfully"
    )


@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Full update a product",
    description="Admin only. Replace all product fields."
)
def full_update(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Full update of a product. **Admin only.**

    All fields are required. Replaces the entire product record.
    """
    product = update_product(db, product_id, payload)
    return success_response(
        data=ProductResponse.model_validate(product).model_dump(mode="json"),
        message="Product updated successfully"
    )


@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Partial update a product",
    description="Admin only. Update only the provided fields."
)
def partial_update(
    product_id: str,
    payload: ProductPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Partial update of a product. **Admin only.**

    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    product = patch_product(db, product_id, payload)
    return success_response(
        data=ProductResponse.model_validate(product).model_dump(mode="json"),
        message="Product patched successfully"
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a product",
    description="Admin only. Soft-delete a product from the catalog."
)
def delete(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Soft-delete a product. **Admin only.**

    Product is marked as inactive, not permanently removed.
    This preserves audit trail and referential integrity.
    """
    result = delete_product(db, product_id)
    return success_response(
        data=None,
        message=result["message"]
    )