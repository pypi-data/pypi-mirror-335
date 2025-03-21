from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid


class BasicAuthUser(BaseModel):
    """Model for basic authentication users."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    roles: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    creator: Optional[str] = None
    modifier: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary excluding password."""
        result = self.model_dump(exclude={"password"})
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        return result


class TokenData(BaseModel):
    """Model for token data."""

    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    exp: Optional[int] = None
    preferred_username: Optional[str] = None
    # Additional fields can be added to support more claims

    def to_dict(self) -> Dict[str, Any]:
        """Convert token data to dictionary."""
        return self.model_dump(exclude_none=True)
