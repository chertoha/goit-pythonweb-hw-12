
"""
This module contains the ContactRepository class responsible for performing database operations
related to contacts using SQLAlchemy's asynchronous session.
"""


from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from schemas import ContactCreate, ContactUpdate, ContactResponse
from datetime import datetime, timedelta



class ContactRepository:
    """
       Repository class for managing contact-related database operations.
    """

    def __init__(self, session: AsyncSession):
        """
               Initialize the repository with a database session.

               :param session: SQLAlchemy AsyncSession instance
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User, search: Optional[str] = None) -> List[Contact]:
        """
                Retrieve a list of contacts for a given user, with optional search filtering.

                :param skip: Number of records to skip
                :param limit: Maximum number of records to return
                :param user: The user who owns the contacts
                :param search: Optional search query for filtering by first name, last name, or email
                :return: List of Contact objects
        """

        stmt = select(Contact).filter_by(user=user)

        if search:
            search_filter = or_(
                Contact.first_name.like(f"%{search}%"),
                Contact.last_name.like(f"%{search}%"),
                Contact.email.like(f"%{search}%")
            )
            stmt = stmt.where(search_filter)

        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
                Retrieve a specific contact by ID for a given user.

                :param contact_id: The ID of the contact to retrieve
                :param user: The user who owns the contact
                :return: Contact object or None if not found
        """

        stmt = select(Contact).filter_by(id=contact_id, user=user)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user: User) -> Contact:
        """
                Create a new contact for the given user.

                :param body: ContactCreate schema containing contact details
                :param user: The user who owns the contact
                :return: Created Contact object
        """

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact


    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
        """
                Update an existing contact for a given user.

                :param contact_id: The ID of the contact to update
                :param body: ContactUpdate schema containing updated fields
                :param user: The user who owns the contact
                :return: Updated Contact object or None if not found
        """

        contact = await self.get_contact_by_id(contact_id, user)

        if contact:
            if body.first_name is not None:
                contact.first_name = body.first_name
            if body.last_name is not None:
                contact.last_name = body.last_name
            if body.email is not None:
                contact.email = body.email
            if body.phone is not None:
                contact.phone = body.phone
            if body.birth_date is not None:
                contact.birth_date = body.birth_date
            if body.additional_data is not None:
                contact.additional_data = body.additional_data

            await self.db.commit()
            await self.db.refresh(contact)

        return contact


    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
                Delete a contact by ID for a given user.

                :param contact_id: The ID of the contact to delete
                :param user: The user who owns the contact
                :return: Deleted Contact object or None if not found
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact



    async def get_contacts_birthday_in_7_days(self, user: User) -> List[Contact]:
        """
                Retrieve contacts whose birthdays are within the next 7 days.

                :param user: The user who owns the contacts
                :return: List of Contact objects with upcoming birthdays
        """

        today = datetime.today()
        seven_days_later = today + timedelta(days=7)

        stmt = select(Contact).filter_by(user=user).filter(
            Contact.birth_date >= today,
            Contact.birth_date <= seven_days_later
        ).order_by(Contact.birth_date)

        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def get_contact_by_email(self, email: str) -> User | None:
        """
                Retrieves a contact by its email address.

                Args:
                    email (str): The email address of the contact to retrieve.

                Returns:
                    User | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(email=email)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()


