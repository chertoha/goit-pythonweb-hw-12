
"""
Module for handling authentication-related operations.

This module contains various functions and classes for implementing authentication,
such as user login, token creation, and token validation. It also provides helper
functions for password hashing and verifying.

Functions:
    - create_access_token: Generates a new JWT access token for the user.
    - get_current_user: Decodes the JWT token and retrieves the current authenticated user.
    - create_email_token: Generates a JWT token for email verification.
    - get_email_from_token: Extracts the email from an email verification token.

Classes:
    - Hash: Provides methods to hash passwords and verify password hashes.
"""
import logging
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.services.users import UserService
from src.conf.config import settings
import json
import redis.asyncio as redis
from src.database.redis import get_redis
from src.database.models import User, UserRole



logging.basicConfig(level=logging.INFO)

class Hash:
    """
        A utility class to handle password hashing and verification.

        This class uses the Passlib library to hash passwords with the bcrypt algorithm
        and to verify the hashed password during authentication.

        Methods:
            - verify_password: Verifies if the plain password matches the hashed password.
            - get_password_hash: Generates a hashed password using bcrypt.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
                Verifies if the given plain password matches the hashed password.

                Args:
                    plain_password (str): The plain password to check.
                    hashed_password (str): The hashed password stored in the database.

                Returns:
                    bool: True if the passwords match, False otherwise.
        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
                Generates a hashed password using bcrypt.

                Args:
                    password (str): The plain password to hash.

                Returns:
                    str: The hashed password.
        """

        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
       Creates a new access token (JWT) for the user.

       This function creates a new JWT token with the specified user data and an expiration time.
       If no expiration time is provided, the default expiration from settings is used.

       Args:
           data (dict): The data (user information) to encode in the token.
           expires_delta (Optional[int], optional): The expiration time in seconds. Defaults to None.

       Returns:
           str: The generated JWT access token.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt



async def create_refresh_token(data: dict, expires_delta: Optional[int] = None):
    """
       Creates a new refresh token (JWT) for the user.

       Args:
           data (dict): The data (user information) to encode in the token.
           expires_delta (Optional[int], optional): The expiration time in seconds. Defaults to None.

       Returns:
           str: The generated JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"exp": expire, "token_type": "refresh"})



    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt




async def verify_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
        Validates the given refresh token and returns the user if valid.

        Args:
            refresh_token (str): The refresh token.
            db (Session): The database session.

        Returns:
            User: The user associated with the refresh token or None if invalid.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_REFRESH_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")


        if username is None or token_type != "refresh":
            return None

        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)

        logging.info(f"verify_refresh_token: user.refresh_token={user.refresh_token}")
        logging.info(f"verify_refresh_token: refresh_token={refresh_token}")

        if refresh_token != user.refresh_token:
            return None


        return user
    except JWTError as err:
        print(f"======JWTError================{err}========================")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), redis: redis.Redis = Depends(get_redis)
):
    """
        Retrieves the currently authenticated user by decoding the JWT token.

        This function decodes the JWT token, extracts the username, and fetches the
        associated user from the database. If the token is invalid or expired,
        an exception is raised.

        Args:
            token (str, optional): The JWT token passed in the Authorization header.
            db (Session, optional): The database session used to retrieve user data.

        Raises:
            HTTPException: If the token is invalid or the user does not exist.

        Returns:
            User: The authenticated user object.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception


    cached_user = await redis.get(f"user:{username}")
    if cached_user:
        user_data = json.loads(cached_user.decode("utf-8"))
        return User(**user_data)

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "confirmed": user.confirmed,
        "avatar": user.avatar,
        "role": user.role
    }
    await redis.set(f"user:{username}", json.dumps(user_data))
    await redis.expire(f"user:{username}", 3600)

    return user


def create_email_token(data: dict):
    """
        Creates an email verification token (JWT) for a given email.

        This function generates a JWT token that contains the email and an expiration time
        (set to 7 days by default). The token can be used for email verification.

        Args:
            data (dict): The data (email) to include in the token.

        Returns:
            str: The generated email verification token.
    """

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str):
    """
        Extracts the email from an email verification token.

        This function decodes the email verification token and retrieves the email address
        from it. If the token is invalid, an HTTP exception is raised.

        Args:
            token (str): The email verification JWT token.

        Raises:
            HTTPException: If the token is invalid or expired.

        Returns:
            str: The email address extracted from the token.
    """

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user