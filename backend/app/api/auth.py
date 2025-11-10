from fastapi import APIRouter

from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthResponse,
)
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
async def register_user(payload: UserRegisterRequest) -> AuthResponse:
    """Register a new user account."""

    user = await user_service.register_user(payload)
    return AuthResponse(user=user)


@router.post("/login", response_model=AuthResponse)
async def login_user(payload: UserLoginRequest) -> AuthResponse:
    """Authenticate an existing user."""

    user = await user_service.authenticate_user(payload)
    return AuthResponse(user=user)
