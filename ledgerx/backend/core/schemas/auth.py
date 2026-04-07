"""Auth request/response schemas."""
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    password: str
    org_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    credential: str


class AppleLoginRequest(BaseModel):
    credential: str


class MicrosoftLoginRequest(BaseModel):
    credential: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str | None
    role: str
    org_id: UUID | None

    class Config:
        from_attributes = True
