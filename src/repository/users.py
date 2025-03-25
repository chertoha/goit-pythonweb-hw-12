"""
Repository module for managing user-related database operations.

This module contains the `UserRepository` class, which provides methods to interact with
the database for CRUD operations related to users. It includes functionalities like
retrieving, creating, and updating user information.

Classes:
    - UserRepository: Handles database interactions related to users.

Methods:
    - get_user_by_id: Retrieves a user by their ID.
    - get_user_by_username: Retrieves a user by their username.
    - get_user_by_email: Retrieves a user by their email.
    - create_user: Creates a new user in the database.
    - confirmed_email: Marks a user's email as confirmed.
    - update_avatar_url: Updates the user's avatar URL.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from schemas import UserCreate

class UserRepository:
    """
        Repository class for managing user-related database operations.

        This class provides methods to interact with the database and perform CRUD operations on
        users, such as retrieving users by their ID, username, or email, creating new users,
        and updating user details.

        Attributes:
            db (AsyncSession): The SQLAlchemy session used for database operations.
    """
    def __init__(self, session: AsyncSession):
        """
                Initializes the UserRepository with the provided database session.

                Args:
                    session (AsyncSession): The SQLAlchemy async session for database operations.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
                Retrieves a user by their ID.

                Args:
                    user_id (int): The ID of the user to retrieve.

                Returns:
                    User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
                Retrieves a user by their username.

                Args:
                    username (str): The username of the user to retrieve.

                Returns:
                    User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
                Retrieves a user by their email address.

                Args:
                    email (str): The email address of the user to retrieve.

                Returns:
                    User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
                Creates a new user in the database.

                Args:
                    body (UserCreate): The data used to create the new user.
                    avatar (Optional[str]): An avatar URL for the user (default is None).

                Returns:
                    User: The created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
                Marks a user's email as confirmed.

                Args:
                    email (str): The email of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()


    async def update_avatar_url(self, email: str, url: str) -> User:
        """
                Updates the avatar URL for a user.

                Args:
                    email (str): The email of the user whose avatar is being updated.
                    url (str): The new avatar URL.

                Returns:
                    User: The user with the updated avatar URL.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
