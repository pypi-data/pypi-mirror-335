import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from fastapi import Depends
from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from passlib.context import CryptContext
import uuid

from zmp_manual_backend.models.auth import BasicAuthUser, TokenData
from zmp_manual_backend.models.exceptions import (
    AuthenticationException,
    ErrorCode,
    ValidationException,
)

logger = logging.getLogger("appLogger")

# In-memory storage for users (replace with database in production)
users_db: Dict[str, BasicAuthUser] = {}
# Add a default admin user
default_admin = BasicAuthUser(
    id=str(uuid.uuid4()),
    username="admin",
    # This is "admin123" hashed (updated with a newly generated hash)
    password="$2b$12$NWMFnBGBobJI.Tv.MH7wzekIxzeO18Gn/6j7EVoZK3DKYDxQ8E3Jm",
    email="admin@example.com",
    full_name="Administrator",
    roles=["admin"],
    creator="system",
)
users_db[default_admin.username] = default_admin

# Password hashing context
# Use only bcrypt to avoid the deprecated 'crypt' module warning
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Explicitly set bcrypt rounds
    bcrypt__default_rounds=12,
)

# JWT settings
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-secret-key-for-jwt-keep-it-secure-in-production"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Setup security schemes
basic_security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    """Service for authentication and user management."""

    def get_basic_auth_users(self) -> List[BasicAuthUser]:
        """Get all basic auth users."""
        return list(users_db.values())

    def get_basic_auth_user_by_username(self, username: str) -> Optional[BasicAuthUser]:
        """Get basic auth user by username."""
        return users_db.get(username)

    def create_basic_auth_user(self, user: BasicAuthUser) -> str:
        """Create a new basic auth user."""
        if user.username in users_db:
            raise ValidationException(
                error_code=ErrorCode.VALIDATION_ERROR,
                detail=f"User with username {user.username} already exists",
            )

        # Hash the password
        user.password = self.get_password_hash(user.password)

        # Set creator if not provided
        if not user.creator:
            user.creator = "system"

        users_db[user.username] = user
        logger.info(f"Created user: {user.username}")
        return user.id

    def remove_basic_auth_user(self, user_id: str) -> None:
        """Remove a basic auth user."""
        for username, user in users_db.items():
            if user.id == user_id:
                del users_db[username]
                logger.info(f"Removed user: {username}")
                return

        raise ValidationException(
            error_code=ErrorCode.USER_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    def modify_basic_auth_user(self, user: BasicAuthUser) -> BasicAuthUser:
        """Modify a basic auth user."""
        existing_user = None
        for _, u in users_db.items():
            if u.id == user.id:
                existing_user = u
                break

        if not existing_user:
            raise ValidationException(
                error_code=ErrorCode.USER_NOT_FOUND,
                detail=f"User with id {user.id} not found",
            )

        # Update password if provided
        if user.password and user.password != existing_user.password:
            user.password = self.get_password_hash(user.password)
        else:
            user.password = existing_user.password

        # Update timestamp
        user.updated_at = datetime.now()

        # Handle username change
        if user.username != existing_user.username:
            if user.username in users_db:
                raise ValidationException(
                    error_code=ErrorCode.VALIDATION_ERROR,
                    detail=f"User with username {user.username} already exists",
                )
            del users_db[existing_user.username]
            users_db[user.username] = user
        else:
            users_db[user.username] = user

        logger.info(f"Modified user: {user.username}")
        return user

    def authenticate_user(self, username: str, password: str) -> BasicAuthUser:
        """Authenticate a user with username and password."""
        user = self.get_basic_auth_user_by_username(username)

        if not user:
            logger.warning(f"Authentication failed: User not found: {username}")
            raise AuthenticationException(
                error_code=ErrorCode.USER_NOT_FOUND,
                detail="Incorrect username or password",
            )

        if not self.verify_password(password, user.password):
            logger.warning(
                f"Authentication failed: Invalid password for user: {username}"
            )
            raise AuthenticationException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                detail="Incorrect username or password",
            )

        if user.disabled:
            logger.warning(f"Authentication failed: Account disabled: {username}")
            raise AuthenticationException(
                error_code=ErrorCode.ACCOUNT_DISABLED, detail="Account is disabled"
            )

        logger.info(f"User authenticated: {username}")
        return user

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        """Verify a JWT token and return the token data."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")

            if username is None:
                logger.warning("Token verification failed: No username in token")
                raise AuthenticationException(
                    error_code=ErrorCode.INVALID_TOKEN,
                    detail="Could not validate credentials",
                )

            token_data = TokenData(
                username=username,
                email=payload.get("email"),
                full_name=payload.get("full_name"),
                roles=payload.get("roles", []),
                exp=payload.get("exp"),
                preferred_username=username,
            )
            return token_data

        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise AuthenticationException(
                error_code=ErrorCode.INVALID_TOKEN,
                detail="Could not validate credentials",
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate a hash for a password."""
        return pwd_context.hash(password)

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme)
    ) -> BasicAuthUser:
        """Get the current authenticated user from the token."""
        token_data = self.verify_token(token)
        user = self.get_basic_auth_user_by_username(token_data.username)

        if user is None:
            logger.warning(f"User not found: {token_data.username}")
            raise AuthenticationException(
                error_code=ErrorCode.USER_NOT_FOUND, detail="User not found"
            )

        return user

    async def get_current_active_user(
        self, current_user: BasicAuthUser = Depends(get_current_user)
    ) -> BasicAuthUser:
        """Check if the current user is active."""
        if current_user.disabled:
            logger.warning(f"Account disabled: {current_user.username}")
            raise AuthenticationException(
                error_code=ErrorCode.ACCOUNT_DISABLED, detail="Account is disabled"
            )

        return current_user


# Create a singleton instance
auth_service = AuthService()
