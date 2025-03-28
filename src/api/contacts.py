"""
API module for handling contact-related endpoints.

This module contains the `contacts` router, which provides endpoints for CRUD operations on contacts.
It includes functionality for managing, updating, deleting, and retrieving contacts, as well as
searching and filtering contacts.

Endpoints:
    - POST /contacts: Creates a new contact.
    - GET /contacts: Retrieves a list of contacts.
    - GET /contacts/{contact_id}: Retrieves a contact by ID.
    - GET /contacts/upcoming-birthdays: Retrieves contacts with birthdays in the next 7 days.
    - PATCH /contacts/{contact_id}: Updates an existing contact by ID.
    - DELETE /contacts/{contact_id}: Deletes a contact by ID.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from schemas import ContactBase,ContactCreate,ContactUpdate, ContactResponse
from src.database.models import User
from src.services.auth import get_current_user
from src.services.contacts import ContactService


router = APIRouter(prefix="/contacts", tags=["contacts"])

# Створити новий контакт
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    print(f"======================{user}=====================")
    """
        Creates a new contact for the current user.

        Args:
            body (ContactCreate): The contact data to create.
            db (AsyncSession): The database session.
            user (User): The current authenticated user.

        Returns:
            ContactResponse: The created contact.
    """
    contact_service = ContactService(db)
    existedContact = await contact_service.get_contact_by_email(body.email)
    if existedContact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Contact with email={body.email} already exists"
        )
    return await contact_service.create_contact(body, user)

# Отримати список всіх контактів
@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
        Retrieves a list of contacts for the current user with optional search functionality.

        Args:
            skip (int): The number of records to skip (for pagination).
            limit (int): The number of records to return.
            search (Optional[str]): The search string to filter contacts by name or email.
            db (AsyncSession): The database session.
            user (User): The current authenticated user.

        Returns:
            List[ContactResponse]: A list of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user, search)
    return contacts

# Отримати контакти, у яких день народження протягом тижня
@router.get("/upcoming-birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
        Retrieves contacts whose birthdays are within the next 7 days.

        Args:
            db (AsyncSession): The database session.
            user (User): The current authenticated user.

        Returns:
            List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_birthday_in_7_days(user)
    return contacts


# Отримати один контакт за ідентифікатором
@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
        Retrieves a contact by its ID for the current user.

        Args:
            contact_id (int): The ID of the contact.
            db (AsyncSession): The database session.
            user (User): The current authenticated user.

        Returns:
            ContactResponse: The contact if found, else raises 404.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

# Оновити контакт, що існує
@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
        Updates an existing contact by ID for the current user.

        Args:
            body (ContactUpdate): The new data for the contact.
            contact_id (int): The ID of the contact to update.
            db (AsyncSession): The database session.
            user (User): The current authenticated user.

        Returns:
            ContactResponse: The updated contact.
    """
    contact_service = ContactService(db)

    if body.email:
        existedContact = await contact_service.get_contact_by_email(body.email)
        if existedContact:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"Contact with email={body.email} already exists"
            )


    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

# Видалити контакт
@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
        Deletes a contact by its ID for the current user.

        Args:
            contact_id (int): The ID of the contact to delete.
            db (AsyncSession): The database session.
            user (User): The current authenticated user.

        Returns:
            ContactResponse: The deleted contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

