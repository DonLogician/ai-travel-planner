from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


USERNAME_REGEX = r"^[A-Za-z0-9]{4,16}$"


class UserRegisterRequest(BaseModel):
    """Request payload for user registration."""

    username: str = Field(
        ...,
        pattern=USERNAME_REGEX,
        description="4-16 characters, letters and numbers only",
    )
    password: str = Field(
        ...,
        pattern=USERNAME_REGEX,
        description="4-16 characters, letters and numbers only",
    )
    confirm_password: str = Field(
        ...,
        pattern=USERNAME_REGEX,
        description="4-16 characters, letters and numbers only",
    )


class UserLoginRequest(BaseModel):
    """Request payload for user login."""

    username: str = Field(..., pattern=USERNAME_REGEX)
    password: str = Field(..., pattern=USERNAME_REGEX)


class UserResponse(BaseModel):
    """Normalized user object returned to the client."""

    id: str
    username: str
    created_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    """Response payload for successful authentication events."""

    user: UserResponse


class VoiceInput(BaseModel):
    """Request model for voice input processing."""

    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="zh_cn", description="Language code")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "base64_encoded_audio_string",
                "language": "zh_cn",
            }
        }


class VoiceResponse(BaseModel):
    """Response model for voice recognition result."""

    text: str = Field(..., description="Recognized text from voice input")
    confidence: Optional[float] = Field(None, description="Confidence score")
