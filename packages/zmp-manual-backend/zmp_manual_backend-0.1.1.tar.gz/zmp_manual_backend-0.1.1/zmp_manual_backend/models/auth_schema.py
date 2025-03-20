from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class BasicAuthUserCreateRequest(BaseModel):
    """Request model for creating a basic auth user."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    roles: List[str] = Field(default_factory=list)


class BasicAuthUserUpdateRequest(BaseModel):
    """Request model for updating a basic auth user."""

    id: str
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: Optional[List[str]] = None


class LoginRequest(BaseModel):
    """Request model for user login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for login token."""

    access_token: str
    token_type: str = "bearer"


class ResponseModel(BaseModel):
    """Generic response model with data field."""

    result: str = "success"
    data: Optional[dict] = None
