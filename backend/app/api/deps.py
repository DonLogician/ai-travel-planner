from fastapi import Depends, Header, HTTPException, status

from app.services.user_service import user_service


async def get_current_user_id(x_user_id: str = Header(default=None)) -> str:
    """Resolve the current user from the custom X-User-ID header."""

    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或会话已过期",
        )

    user = await user_service.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户身份无效，请重新登录",
        )

    return user.id
