from enum import Enum
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class ErrorCode(str, Enum):
    """Error codes for the application."""

    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class AuthenticationException(HTTPException):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Authentication error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        if not headers:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=status_code,
            detail={"error_code": error_code, "message": detail},
            headers=headers,
        )


class AuthorizationException(HTTPException):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.AUTHORIZATION_ERROR,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "Not authorized to perform this action",
    ):
        super().__init__(
            status_code=status_code,
            detail={"error_code": error_code, "message": detail},
        )


class ValidationException(HTTPException):
    """Exception raised for data validation errors."""

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Data validation error",
    ):
        super().__init__(
            status_code=status_code,
            detail={"error_code": error_code, "message": detail},
        )
