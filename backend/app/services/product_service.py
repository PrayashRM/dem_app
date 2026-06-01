from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductPatch
from app.utils.exceptions import NotFoundException, BadRequestException
import logging

logger = logging.getLogger(__name__)


def create_product(db: Session, payload: ProductCreate, current_user: User) -> Product:
    """Create a new product. Admin only."""
    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        category=payload.category,
        created_by=current_user.id,
        is_active=True
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info(f"Product created: {product.id} by user {current_user.id}")
        return product
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}")
        raise


def get_products(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None
) -> dict:
    """
    Get paginated list of active products.
    Supports search, category filter, price range, and stock filter.
    """
    # Validate pagination params
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    query = db.query(Product).filter(Product.is_active == True)

    # Search across name and description
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )

    # Category filter
    if category:
        query = query.filter(Product.category.ilike(f"%{category.strip()}%"))

    # Price range filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Stock filter
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock > 0)
        else:
            query = query.filter(Product.stock == 0)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()

    total_pages = (total + limit - 1) // limit

    return {
        "items": products,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }


def get_product_by_id(db: Session, product_id: str) -> Product:
    """Get a single active product by ID."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise NotFoundException("Product")

    return product


def update_product(db: Session, product_id: str, payload: ProductUpdate) -> Product:
    """Full update of a product. Admin only."""
    product = get_product_by_id(db, product_id)

    product.name = payload.name
    product.description = payload.description
    product.price = payload.price
    product.stock = payload.stock
    product.category = payload.category

    try:
        db.commit()
        db.refresh(product)
        logger.info(f"Product updated: {product.id}")
        return product
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product: {e}")
        raise


def patch_product(db: Session, product_id: str, payload: ProductPatch) -> Product:
    """Partial update of a product. Admin only."""
    product = get_product_by_id(db, product_id)

    # Only update fields that were explicitly provided
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise BadRequestException("No fields provided to update")

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
        logger.info(f"Product patched: {product.id} — fields: {list(update_data.keys())}")
        return product
    except Exception as e:
        db.rollback()
        logger.error(f"Error patching product: {e}")
        raise


def delete_product(db: Session, product_id: str) -> dict:
    """
    Soft delete a product by setting is_active to False.
    This preserves data integrity and audit trail.
    """
    product = get_product_by_id(db, product_id)
    product.is_active = False

    try:
        db.commit()
        logger.info(f"Product soft-deleted: {product_id}")
        return {"message": "Product deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting product: {e}")
        raise