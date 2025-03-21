from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

import logging
from datetime import timedelta

from zmp_manual_backend.core.auth_service import (
    auth_service,
    oauth2_scheme,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from zmp_manual_backend.models.auth import BasicAuthUser, TokenData
from zmp_manual_backend.models.auth_schema import (
    BasicAuthUserCreateRequest,
    BasicAuthUserUpdateRequest,
    LoginRequest,
    TokenResponse,
    ResponseModel,
)

logger = logging.getLogger("appLogger")

router = APIRouter()


def get_current_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Get the current token data from the token."""
    return auth_service.verify_token(token)


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Token endpoint for OAuth2 password flow."""
    user = auth_service.authenticate_user(form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={
            "sub": user.username,
            "roles": user.roles,
            "email": user.email,
            "full_name": user.full_name,
        },
        expires_delta=access_token_expires,
    )

    logger.info(f"Generated token for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Login endpoint for custom login form."""
    user = auth_service.authenticate_user(login_data.username, login_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={
            "sub": user.username,
            "roles": user.roles,
            "email": user.email,
            "full_name": user.full_name,
        },
        expires_delta=access_token_expires,
    )

    logger.info(f"Generated token for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=TokenData)
async def read_users_me(current_user: TokenData = Depends(get_current_token_data)):
    """Get current user information."""
    return current_user


@router.get("/basic_auth_users", response_model=List[BasicAuthUser])
async def get_basic_auth_users(
    current_user: TokenData = Depends(get_current_token_data),
) -> List[BasicAuthUser]:
    """Get all basic auth users."""
    # Check if user has admin role
    if "admin" not in current_user.roles:
        logger.warning(
            f"Unauthorized access attempt to user list by: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    users = auth_service.get_basic_auth_users()
    # Convert to response by excluding passwords
    return [BasicAuthUser(**u.model_dump(exclude={"password"})) for u in users]


@router.post("/basic_auth_users", response_model=ResponseModel)
async def create_basic_auth_user(
    user_data: BasicAuthUserCreateRequest,
    current_user: TokenData = Depends(get_current_token_data),
) -> ResponseModel:
    """Create a new basic auth user."""
    # Check if user has admin role
    if "admin" not in current_user.roles:
        logger.warning(f"Unauthorized create user attempt by: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = BasicAuthUser(**user_data.model_dump())
    user.creator = current_user.username

    user_id = auth_service.create_basic_auth_user(user)
    return ResponseModel(data={"id": user_id})


@router.get("/basic_auth_users/{username}", response_model=BasicAuthUser)
async def get_basic_auth_user_by_username(
    username: str, current_user: TokenData = Depends(get_current_token_data)
) -> BasicAuthUser:
    """Get basic auth user by username."""
    # Users can only see their own info unless they're admin
    if username != current_user.username and "admin" not in current_user.roles:
        logger.warning(
            f"Unauthorized access attempt to user {username} by: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = auth_service.get_basic_auth_user_by_username(username)
    if not user:
        logger.warning(f"User not found: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Exclude password from response
    return BasicAuthUser(**user.model_dump(exclude={"password"}))


@router.delete("/basic_auth_users/{id}", response_model=ResponseModel)
async def remove_basic_auth_user(
    id: str, current_user: TokenData = Depends(get_current_token_data)
) -> ResponseModel:
    """Remove a basic auth user."""
    # Check if user has admin role
    if "admin" not in current_user.roles:
        logger.warning(f"Unauthorized delete user attempt by: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    auth_service.remove_basic_auth_user(id)
    return ResponseModel(data={"message": "User deleted successfully"})


@router.put("/basic_auth_users", response_model=BasicAuthUser)
async def modify_basic_auth_user(
    user_data: BasicAuthUserUpdateRequest,
    current_user: TokenData = Depends(get_current_token_data),
) -> BasicAuthUser:
    """Modify a basic auth user."""
    # Get existing user
    existing_user = None
    for user in auth_service.get_basic_auth_users():
        if user.id == user_data.id:
            existing_user = user
            break

    if not existing_user:
        logger.warning(f"User not found: ID {user_data.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Users can only modify their own info unless they're admin
    if (
        existing_user.username != current_user.username
        and "admin" not in current_user.roles
    ):
        logger.warning(
            f"Unauthorized modification attempt to user {existing_user.username} by: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Non-admins can't change their roles
    if "admin" not in current_user.roles and user_data.roles is not None:
        user_data.roles = existing_user.roles

    user = BasicAuthUser(**user_data.model_dump(exclude_unset=True))
    user.modifier = current_user.username

    updated_user = auth_service.modify_basic_auth_user(user)
    # Exclude password from response
    return BasicAuthUser(**updated_user.model_dump(exclude={"password"}))
