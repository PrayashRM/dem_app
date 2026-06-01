from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.utils.exceptions import (
    ConflictException,
    UnauthorizedException,
    BadRequestException,
    ForbiddenException        
)
import logging

logger = logging.getLogger(__name__)

_DUMMY_HASH = "$2b$12$KIXnHu3TXtBgJ0WsNb2T4.7QZ1vLwIqlR5RoFBgMWe2JR/LJq2g3i"


def register_user(db: Session, payload: UserCreate) -> User:
    """
    Register a new user.
    Checks for duplicate email before creating.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == payload.email.lower()
    ).first()

    if existing_user:
        raise ConflictException("An account with this email already exists")

    # Create new user
    new_user = User(
        email=payload.email.lower().strip(),
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        role=UserRole.USER,
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"New user registered: {new_user.email}")
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise


def login_user(db: Session, payload: UserLogin) -> dict:
    """
    Authenticate user and return JWT token.
    Performs constant-time password verification.
    """
    user = db.query(User).filter(
        User.email == payload.email.lower()
    ).first()

    # Always verify password even if user not found
    # This prevents timing attacks that reveal valid emails
    password_to_verify = user.hashed_password if user else _DUMMY_HASH

    is_valid = verify_password(payload.password, password_to_verify)

    if not user or not is_valid:
        raise UnauthorizedException("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException(
            "Your account has been deactivated. Please contact support"
        )

    # Create JWT token
    role_value = (
        user.role
        if isinstance(user.role, str)
        else user.role.value
    )

    access_token = create_access_token(
        subject=user.id,
        role=role_value,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"User logged in: {user.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }