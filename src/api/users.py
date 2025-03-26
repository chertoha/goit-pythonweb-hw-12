"""
API module for handling user-related endpoints.

This module contains the `users` router, which provides endpoints for user profile operations,
such as retrieving the current user's information and updating the avatar.

Endpoints:
    - GET /users/me: Retrieves the current authenticated user's information.
    - PATCH /users/avatar: Updates the current user's avatar.
"""

from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

from schemas import User
from src.conf.config import settings
from src.services.auth import get_current_user, get_current_admin_user
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])

limiter = Limiter(key_func=get_remote_address)



@router.get("/me", response_model=User)
@limiter.limit("60/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
        Retrieves the current authenticated user's profile information.

        Args:
            request (Request): The request object.
            user (User): The currently authenticated user.

        Returns:
            User: The authenticated user.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
        Updates the current user's avatar with a new file.

        Args:
            file (UploadFile): The new avatar file.
            user (User): The current authenticated user.
            db (AsyncSession): The database session.

        Returns:
            User: The updated user with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user