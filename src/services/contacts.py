"""
Module for managing contacts in the application.

This module handles operations related to contacts, such as creating, updating,
retrieving, and deleting contacts. It interacts with the repository layer to perform
database operations and return contact data. The module also includes logic to fetch
contacts whose birthdays are approaching in the next 7 days.

Classes:
    - ContactService: Provides methods for managing contacts, including CRUD operations.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import ContactRepository
from schemas import  ContactCreate, ContactUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from src.database.models import User


class ContactService:
    """
        Service class for managing user contacts.

        This class provides methods for creating, retrieving, updating, and deleting contacts
        in the system. It interacts with the repository layer to perform database operations
        and manage contacts effectively.

        Methods:
            - create_contact: Creates a new contact for the user.
            - get_contacts: Retrieves a list of contacts with pagination and optional search.
            - get_contact: Retrieves a specific contact by ID.
            - update_contact: Updates an existing contact's details.
            - remove_contact: Deletes a contact by ID.
            - get_contacts_birthday_in_7_days: Retrieves contacts whose birthdays are in the next 7 days.
            - get_contact_by_email: Retrieves a contact by their email address.
    """

    def __init__(self, db: AsyncSession):
        """
                Initializes the ContactService with the provided database session.

                Args:
                    db (AsyncSession): The database session to interact with the repository.
        """

        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user: User):
        """
                Creates a new contact for the specified user.

                Args:
                    body (ContactCreate): The contact data for the new contact.
                    user (User): The user to associate with the contact.

                Returns:
                    Contact: The newly created contact.
        """
        return await self.repository.create_contact(body, user)


    async def get_contacts(self, skip: int, limit: int, user: User, search: Optional[str] = None):
        """
                Retrieves a list of contacts for the specified user with pagination and optional search.

                Args:
                    skip (int): The number of contacts to skip.
                    limit (int): The maximum number of contacts to return.
                    user (User): The user whose contacts are to be retrieved.
                    search (Optional[str], optional): A search query to filter contacts by name or email. Defaults to None.

                Returns:
                    List[Contact]: A list of contacts matching the specified parameters.
        """
        return await self.repository.get_contacts(skip, limit, user, search)



    async def get_contact(self, contact_id: int, user: User):
        """
                Retrieves a specific contact by its ID.

                Args:
                    contact_id (int): The ID of the contact to retrieve.
                    user (User): The user associated with the contact.

                Returns:
                    Contact: The contact object, or None if no contact is found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)



    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """
                Updates the details of an existing contact.

                Args:
                    contact_id (int): The ID of the contact to update.
                    body (ContactUpdate): The updated contact data.
                    user (User): The user associated with the contact.

                Returns:
                    Contact: The updated contact, or None if no contact is found to update.
        """
        return await self.repository.update_contact(contact_id, body, user)



    async def remove_contact(self, contact_id: int, user: User):
        """
                Removes a contact by its ID.

                Args:
                    contact_id (int): The ID of the contact to remove.
                    user (User): The user associated with the contact.

                Returns:
                    Contact: The removed contact, or None if no contact was found.
        """
        return await self.repository.remove_contact(contact_id, user)



    async def get_contacts_birthday_in_7_days(self, user: User):
        """
               Retrieves contacts whose birthdays are in the next 7 days.

               Args:
                   user (User): The user whose contacts' birthdays are to be checked.

               Returns:
                   List[Contact]: A list of contacts with birthdays in the next 7 days.
        """
        return await self.repository.get_contacts_birthday_in_7_days(user)


    async def get_contact_by_email(self, email: str):
        """
                Retrieves a contact by its email address.

                Args:
                    email (str): The email address of the contact.

                Returns:
                    Contact: The contact with the specified email address, or None if no contact is found.
        """
        return await self.repository.get_contact_by_email(email)