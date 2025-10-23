from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class VoiceInput(BaseModel):
    """Request model for voice input processing."""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="zh_cn", description="Language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "base64_encoded_audio_string",
                "language": "zh_cn"
            }
        }


class VoiceResponse(BaseModel):
    """Response model for voice recognition result."""
    text: str = Field(..., description="Recognized text from voice input")
    confidence: Optional[float] = Field(None, description="Confidence score")
