from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, login_user
from app.dependencies.auth import get_current_active_user
from app.utils.responses import success_response
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, full name, and password."
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **full_name**: 2–100 characters, alphabetic only
    - **password**: Min 8 chars, must include uppercase, lowercase, and digit
    """
    user = register_user(db, payload)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(mode="json"),
        message="Account created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login and get JWT token",
    description="Authenticate with email and password to receive a JWT access token."
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    - **email**: Registered email address
    - **password**: Account password

    Returns a Bearer token to use in protected endpoints.
    """
    token_data = login_user(db, payload)
    return success_response(
        data={
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
            "expires_in": token_data["expires_in"],
            "user": UserResponse.model_validate(token_data["user"]).model_dump(mode="json")
        },
        message="Login successful"
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user."
)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the authenticated user's profile.

    Requires a valid Bearer token in the Authorization header.
    """
    return success_response(
        data=UserResponse.model_validate(current_user).model_dump(mode="json"),
        message="Profile retrieved successfully"
    )