from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Product name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Product description"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Product price must be greater than 0"
    )
    stock: int = Field(
        ...,
        ge=0,
        description="Stock quantity must be 0 or greater"
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Product category"
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Wireless Headphones",
                "description": "Premium noise-cancelling headphones",
                "price": 299.99,
                "stock": 50,
                "category": "Electronics"
            }
        }
    }


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=50)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Headphones",
                "description": "Updated description",
                "price": 249.99,
                "stock": 75,
                "category": "Electronics"
            }
        }
    }


class ProductPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "price": 199.99,
                "stock": 100
            }
        }
    }


class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_previous: bool