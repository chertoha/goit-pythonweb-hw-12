"""
SQLAlchemy database models module.

This module defines the database models used in the application, including the `User` and `Contact` models
for handling user and contact data in the database.

Classes:
    - Contact: SQLAlchemy model representing a user's contact.
    - User: SQLAlchemy model representing a user.
"""
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, func, Enum as SqlEnum
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Contact(Base):
    """
        SQLAlchemy model representing a user's contact.

        Attributes:
            id (int): Unique identifier for the contact.
            first_name (str): First name of the contact.
            last_name (str): Last name of the contact.
            email (str): Email address of the contact.
            phone (str): Phone number of the contact.
            birth_date (Date): Birth date of the contact.
            additional_data (str | None): Additional data for the contact (optional).
            user_id (int | None): Foreign key to the associated user.
            user (User): Relationship to the associated user.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    birth_date = Column(Date)
    additional_data = Column(String, nullable=True)
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None)
    user = relationship("User", backref="contacts")


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    """
        SQLAlchemy model representing a user.

        Attributes:
            id (int): Unique identifier for the user.
            username (str): Username of the user.
            email (str): Email address of the user.
            hashed_password (str): The hashed password for the user.
            created_at (DateTime): Timestamp of when the user was created.
            avatar (str | None): URL of the user's avatar image.
            confirmed (bool): Flag indicating whether the user's email has been confirmed.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    refresh_token = Column(String(255), nullable=True)


