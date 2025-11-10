from typing import Optional
from fastapi import HTTPException, status

from app.core.database import get_supabase_client
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse


class UserService:
    """Service layer handling user storage and authentication."""

    def __init__(self) -> None:
        self.supabase = get_supabase_client()
        self.table = "users"

    async def register_user(self, payload: UserRegisterRequest) -> UserResponse:
        """Create a new user record after validating uniqueness."""

        username = payload.username.strip()
        if payload.password != payload.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致",
            )

        existing = (
            self.supabase.table(self.table)
            .select("user_id")
            .eq("user_id", username)
            .limit(1)
            .execute()
        )
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )

        insert_payload = {
            "user_id": username,
            "password": payload.password,
        }

        result = self.supabase.table(self.table).insert(insert_payload).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册用户失败，请稍后再试",
            )

        record = result.data[0]
        return UserResponse(
            id=str(record.get("user_id", username)),
            username=record.get("user_id", username),
            created_at=None,
        )

    async def authenticate_user(self, payload: UserLoginRequest) -> UserResponse:
        """Validate provided credentials and return the user."""

        result = (
            self.supabase.table(self.table)
            .select("user_id, password")
            .eq("user_id", payload.username.strip())
            .eq("password", payload.password)
            .limit(1)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        record = result.data[0]
        return UserResponse(
            id=str(record.get("user_id", payload.username.strip())),
            username=record.get("user_id", payload.username.strip()),
            created_at=None,
        )

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Fetch a user by identifier, returning None when missing."""

        result = (
            self.supabase.table(self.table)
            .select("user_id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        record = result.data[0]
        return UserResponse(
            id=str(record.get("user_id", "")),
            username=record.get("user_id", ""),
            created_at=None,
        )


user_service = UserService()
