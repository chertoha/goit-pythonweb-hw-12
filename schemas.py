from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, condecimal, constr, ConfigDict


class ContactBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: str = Field(..., max_length=15)
    birth_date: datetime
    additional_data: Optional[str] = None

    class Config:
        orm_mode = True

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    birth_date: Optional[datetime] = None
    additional_data: Optional[str] = None

    class Config:
        orm_mode = True

class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True


# Схема користувача
class User(BaseModel):
    id: int
    username: str
    # email: str
    email: EmailStr = Field(..., max_length=100)
    avatar: str

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    # email: str
    email: EmailStr = Field(..., max_length=100)
    password: str

# Схема для токену
class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr