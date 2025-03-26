"""
API module for handling authentication and user registration.

This module contains the `auth` router, which provides endpoints for user registration, login,
email confirmation, and password resetting. It includes endpoints to authenticate users, create
access tokens, and send confirmation emails.

Endpoints:
    - POST /register: Registers a new user.
    - POST /login: Authenticates a user and returns an access token.
    - GET /confirmed_email/{token}: Confirms a user's email address.
    - POST /request_email: Requests a new confirmation email.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email
from src.database.redis import get_redis
import json
import redis.asyncio as redis

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
        Registers a new user and sends a confirmation email.

        Args:
            user_data (UserCreate): The data for the new user.
            background_tasks (BackgroundTasks): The background tasks to send email.
            request (Request): The request to base the email URL on.
            db (Session): The database session.

        Returns:
            User: The newly created user.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), redis: redis.Redis = Depends(get_redis)
):
    """
        Authenticates a user and returns an access token.

        Args:
            form_data (OAuth2PasswordRequestForm): The login credentials.
            db (Session): The database session.
            redis (redis.Redis): The Redis cache.

        Returns:
            Token: The access token.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = await create_access_token(data={"sub": user.username})

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "confirmed": user.confirmed,
        "avatar": user.avatar,
    }

    await redis.set(f"user:{user.username}", json.dumps(user_data))
    await redis.expire(f"user:{user.username}", 3600)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
        Confirms a user's email address.

        Args:
            token (str): The confirmation token.
            db (Session): The database session.

        Returns:
            dict: A message indicating whether the email has been confirmed.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ваша електронна пошта вже підтверджена"
        )


    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
        Resends the email verification link if the user's email is not confirmed.

        Args:
            body (RequestEmail): Email address for verification.
            background_tasks (BackgroundTasks): Task to send email.
            request (Request): Request object to generate confirmation URL.
            db (Session): Database session.

        Returns:
            dict: Confirmation message or a message indicating the email is already confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


