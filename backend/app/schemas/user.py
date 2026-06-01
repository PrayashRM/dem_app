from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Password must be at least 8 characters"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v.replace(" ", "").isalpha():
            raise ValueError("Full name must contain only alphabetic characters")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "SecurePass123"
            }
        }
    }


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@example.com",
                "password": "Admin123"
            }
        }
    }


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None