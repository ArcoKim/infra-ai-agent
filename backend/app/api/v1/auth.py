from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_mysql_session
from app.core.security import get_current_user_id
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate,
    LoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(
    request: UserCreate,
    db: AsyncSession = Depends(get_mysql_session)
):
    """Register a new user."""
    service = AuthService(db)
    return await service.register(request)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_mysql_session)
):
    """Login and get access token."""
    service = AuthService(db)
    return await service.login(request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_mysql_session)
):
    """Refresh access token."""
    service = AuthService(db)
    return await service.refresh(request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """Get current user info."""
    service = AuthService(db)
    return await service.get_current_user(user_id)


@router.post("/logout")
async def logout(
    user_id: str = Depends(get_current_user_id)
):
    """Logout (client should discard tokens)."""
    return {"message": "Successfully logged out"}
