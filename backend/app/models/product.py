from sqlalchemy import (
    Column, String, Text, Float,
    Integer, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    name = Column(
        String(100),
        nullable=False,
        index=True
    )
    description = Column(
        Text,
        nullable=True
    )
    price = Column(
        Float,
        nullable=False
    )
    stock = Column(
        Integer,
        nullable=False,
        default=0
    )
    category = Column(
        String(50),
        nullable=True,
        index=True
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    created_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    creator = relationship(
        "User",
        back_populates="products"
    )

    # Composite index for common query patterns
    __table_args__ = (
        Index("idx_products_name_category", "name", "category"),
        Index("idx_products_active_created", "is_active", "created_at"),
    )

    def __repr__(self):
        return f"<Product id={self.id} name={self.name} price={self.price}>"