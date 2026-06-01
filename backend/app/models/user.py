from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
import enum
import uuid
from app.database.db import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


# create_type=False tells SQLAlchemy to never auto-create this ENUM
# Alembic owns the ENUM lifecycle entirely
user_role_enum = ENUM(
    UserRole,
    name="userrole",
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)


class User(Base):
    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    full_name = Column(
        String(100),
        nullable=False
    )
    hashed_password = Column(
        String(255),
        nullable=False
    )
    role = Column(
        user_role_enum,
        default=UserRole.USER,
        nullable=False,
        index=True
    )
    is_active = Column(
        Boolean,
        default=True,
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
    products = relationship(
        "Product",
        back_populates="creator",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"