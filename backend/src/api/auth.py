"""Authentication API router.

Provides endpoints for user registration, login, logout, and verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response schemas
class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str | None = Field(None, max_length=100)


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User data response."""

    id: str
    email: str
    display_name: str | None
    language_pref: str
    is_verified: bool

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Authentication response with user and token."""

    user: UserResponse
    token: TokenResponse


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Register a new user account.

    Args:
        request: Registration details.
        db: Database session.

    Returns:
        Created user with access token.

    Raises:
        HTTPException: If email is already registered.
    """
    auth_service = AuthService(db)

    try:
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    token = AuthService.create_access_token(user.id)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=TokenResponse(access_token=token),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Login with email and password.

    Args:
        request: Login credentials.
        db: Database session.

    Returns:
        User data with access token.

    Raises:
        HTTPException: If credentials are invalid.
    """
    auth_service = AuthService(db)
    result = await auth_service.login(request.email, request.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user, token = result

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=TokenResponse(access_token=token),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Logout the current user.

    Note: Since we use stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint exists for API completeness.

    Args:
        user: Current authenticated user.

    Returns:
        Success message.
    """
    return MessageResponse(message="Successfully logged out")


@router.get("/verify", response_model=UserResponse)
async def verify(
    user: User = Depends(get_current_user),
) -> UserResponse:
    """Verify the current access token and return user data.

    Args:
        user: Current authenticated user.

    Returns:
        Current user data.
    """
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user profile.

    Args:
        user: Current authenticated user.

    Returns:
        Current user data.
    """
    return UserResponse.model_validate(user)
