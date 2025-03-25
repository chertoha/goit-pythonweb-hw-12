import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from schemas import ContactCreate, ContactUpdate, ContactResponse


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [Contact(id=1, first_name="John", last_name="Doe", user=user)]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(id=1, first_name="John", last_name="Doe", user=user)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        birth_date="2000-01-01"
    )

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactUpdate(first_name="Updated John", last_name="Updated Doe")
    existing_contact = Contact(id=1, first_name="John", last_name="Doe", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(contact_id=1, body=contact_data, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "Updated John"
    assert result.last_name == "Updated Doe"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(id=1, first_name="John", last_name="Doe", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_contacts_birthday_in_7_days(contact_repository, mock_session, user):
    # Setup
    today = datetime.today()
    seven_days_later = today + timedelta(days=7)

    contact_data = Contact(id=1, first_name="John", last_name="Doe", user=user, birth_date=today + timedelta(days=5))
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact_data]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts_birthday_in_7_days(user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].birth_date <= seven_days_later


@pytest.mark.asyncio
async def test_get_contact_by_email(contact_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_email(email="john@example.com")

    # Assertions
    assert contact is not None
    assert contact.email == "john@example.com"
