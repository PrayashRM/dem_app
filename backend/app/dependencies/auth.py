from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.utils.exceptions import UnauthorizedException, ForbiddenException

# Use HTTPBearer for cleaner Swagger UI
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract and validate the current authenticated user.
    Raises 401 if token is missing or invalid.
    """
    if not credentials:
        raise UnauthorizedException("Authentication token is required")

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()

    if not user:
        raise UnauthorizedException("User not found or account is inactive")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure user is active."""
    if not current_user.is_active:
        raise ForbiddenException("Your account has been deactivated")
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to restrict endpoint access to admin users only.
    Raises 403 if user is not admin.
    """
    role_value = (
        current_user.role
        if isinstance(current_user.role, str)
        else current_user.role.value
    )
    if role_value != UserRole.ADMIN.value:
        raise ForbiddenException("Admin privileges required for this action")
    
    return current_user