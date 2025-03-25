"""
Pydantic schemas for data validation.

This module defines the Pydantic schemas used to validate incoming data and provide response models
for contacts and users. It includes validation for user registration, contact creation, and updates.

Classes:
    - ContactBase: Base schema for contact data validation.
    - ContactCreate: Schema for creating a new contact.
    - ContactUpdate: Schema for updating an existing contact.
    - ContactResponse: Response schema for contacts.
    - User: Schema for user data.
    - UserCreate: Schema for user registration data.
    - Token: Schema for the access token.
    - RequestEmail: Schema for requesting email confirmation.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, condecimal, constr, ConfigDict


class ContactBase(BaseModel):
    """
        Base schema for contact data validation.

        Attributes:
            first_name (str): First name of the contact.
            last_name (str): Last name of the contact.
            email (EmailStr): Email address of the contact.
            phone (str): Phone number of the contact.
            birth_date (datetime): Birth date of the contact.
            additional_data (str | None): Additional data for the contact (optional).
    """
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: str = Field(..., max_length=15)
    birth_date: datetime
    additional_data: Optional[str] = None

    class Config:
        orm_mode = True

class ContactCreate(ContactBase):
    """
        Schema for creating a new contact.

        This schema inherits from ContactBase and does not add new fields,
        but is used specifically for contact creation requests.
    """
    pass

class ContactUpdate(BaseModel):
    """
            Schema for updating an existing contact.

            Attributes:
                first_name (Optional[str]): Optional updated first name for the contact.
                last_name (Optional[str]): Optional updated last name for the contact.
                email (Optional[EmailStr]): Optional updated email address for the contact.
                phone (Optional[str]): Optional updated phone number for the contact.
                birth_date (Optional[datetime]): Optional updated birth date for the contact.
                additional_data (Optional[str]): Optional additional data for the contact.
    """
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    birth_date: Optional[datetime] = None
    additional_data: Optional[str] = None

    class Config:
        orm_mode = True

class ContactResponse(ContactBase):
    """
            Response schema for contacts.

            This schema extends ContactBase and adds the 'id' field to return
            the contact information with a unique identifier.

            Attributes:
                id (int): Unique identifier for the contact.
    """
    id: int

    class Config:
        orm_mode = True


# Схема користувача
class User(BaseModel):
    """
            Schema for user data.

            Attributes:
                id (int): Unique identifier for the user.
                username (str): Username of the user.
                email (EmailStr): Email address of the user.
                avatar (str): Avatar image URL for the user.
    """
    id: int
    username: str
    email: EmailStr = Field(..., max_length=100)
    avatar: str

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    """
        Schema for user registration data.

        Attributes:
            username (str): The username of the new user.
            email (EmailStr): The email address of the new user.
            password (str): The password for the new user.
    """
    username: str
    email: EmailStr = Field(..., max_length=100)
    password: str

# Схема для токену
class Token(BaseModel):
    """
        Schema for the access token response.

        Attributes:
            access_token (str): The JWT access token.
            token_type (str): The type of the token (usually "bearer").
    """
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr