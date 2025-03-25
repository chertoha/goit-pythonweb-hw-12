"""
Module for handling user-related operations.

This module provides services for user-related functionality, such as creating
users, retrieving user details, and updating user information. It interfaces with
the UserRepository to interact with the database for CRUD operations on users.

Classes:
    - UserService: Contains methods for managing user data in the system.

Methods:
    - create_user: Creates a new user in the system, including fetching a gravatar image.
    - get_user_by_id: Retrieves a user by their unique ID.
    - get_user_by_username: Retrieves a user by their username.
    - get_user_by_email: Retrieves a user by their email.
    - confirmed_email: Confirms a user's email address after verification.
    - update_avatar_url: Updates the user's avatar URL.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from schemas import UserCreate

class UserService:
    """
        Service for handling user-related operations.

        This service provides methods to interact with user data, including
        creating new users, retrieving user information, confirming email addresses,
        and updating user avatars.
    """
    def __init__(self, db: AsyncSession):
        """
                Initializes the UserService with a database session.

                Args:
                    db (AsyncSession): The SQLAlchemy session for database operations.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
                Creates a new user and optionally fetches a gravatar image for the user.

                The user is created with the provided details, and an avatar image is fetched
                from Gravatar based on the user's email. If fetching the gravatar fails, the
                user will be created without an avatar.

                Args:
                    body (UserCreate): The user details for creating the user.

                Returns:
                    User: The created user.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
                Retrieves a user by their unique ID.

                Args:
                    user_id (int): The ID of the user to retrieve.

                Returns:
                    User | None: The user with the specified ID, or None if not found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
                Retrieves a user by their username.

                Args:
                    username (str): The username of the user to retrieve.

                Returns:
                    User | None: The user with the specified username, or None if not found.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
                Retrieves a user by their email.

                Args:
                    email (str): The email of the user to retrieve.

                Returns:
                    User | None: The user with the specified email, or None if not found.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
                Confirms a user's email address.

                This method is typically called after the user clicks a confirmation link sent
                to their email. It updates the user's confirmation status in the database.

                Args:
                    email (str): The email address of the user to confirm.

                Returns:
                    None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
                Updates a user's avatar URL.

                This method is used to update the user's profile with a new avatar image.

                Args:
                    email (str): The email address of the user whose avatar is to be updated.
                    url (str): The new avatar URL.

                Returns:
                    User: The user with the updated avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)

