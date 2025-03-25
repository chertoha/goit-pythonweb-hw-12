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
    # contact_data = ContactCreate(first_name="John", last_name="Doe", email="john@example.com")
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",  # Добавляем обязательное поле
        birth_date="2000-01-01"  # Добавляем обязательное поле
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

#
# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.database.models import User
# from src.repository.users import UserRepository
# from schemas import UserCreate
#
#
# @pytest.fixture
# def mock_session():
#     return AsyncMock(spec=AsyncSession)
#
#
# @pytest.fixture
# def user_repository(mock_session):
#     return UserRepository(mock_session)
#
#
# @pytest.fixture
# def user():
#     return User(id=1, username="testuser", email="test@example.com", confirmed=False)
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_id(user_repository, mock_session, user):
#     # Setup mock
#     mock_result = AsyncMock()
#     mock_result.scalar_one_or_none.return_value = user
#     mock_session.execute.return_value = mock_result
#
#     # Call method
#     result = await user_repository.get_user_by_id(user_id=1)
#
#     # Assertions
#     assert result is not None
#     assert result.id == 1
#     assert result.username == "testuser"
#     assert result.email == "test@example.com"
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_username(user_repository, mock_session, user):
#     # Setup mock
#     mock_result = AsyncMock()
#     mock_result.scalar_one_or_none.return_value = user
#     mock_session.execute.return_value = mock_result
#
#     # Call method
#     result = await user_repository.get_user_by_username(username="testuser")
#
#     # Assertions
#     assert result is not None
#     assert result.username == "testuser"
#     assert result.email == "test@example.com"
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_email(user_repository, mock_session, user):
#     # Setup mock
#     mock_result = AsyncMock()
#     mock_result.scalar_one_or_none.return_value = user
#     mock_session.execute.return_value = mock_result
#
#     # Call method
#     result = await user_repository.get_user_by_email(email="test@example.com")
#
#     # Assertions
#     assert result is not None
#     assert result.email == "test@example.com"
#     assert result.username == "testuser"
#
#
# @pytest.mark.asyncio
# async def test_create_user(user_repository, mock_session):
#     # Setup
#     user_data = UserCreate(
#         username="newuser",
#         email="new@example.com",
#         password="securepassword"
#     )
#
#     # Call method
#     result = await user_repository.create_user(body=user_data, avatar="http://example.com/avatar.png")
#
#     # Assertions
#     assert isinstance(result, User)
#     assert result.username == "newuser"
#     assert result.email == "new@example.com"
#     assert result.avatar == "http://example.com/avatar.png"
#     mock_session.add.assert_called_once()
#     mock_session.commit.assert_awaited_once()
#     mock_session.refresh.assert_awaited_once_with(result)
#
#
# @pytest.mark.asyncio
# async def test_confirmed_email(user_repository, mock_session, user):
#     # Setup
#     user.confirmed = False
#
#     mock_session.execute.return_value = AsyncMock(return_value=user)  # Use AsyncMock correctly
#
#     await user_repository.confirmed_email(email="test@example.com")
#
#     assert user.confirmed is True
#     mock_session.commit.assert_awaited_once()
#
#
# @pytest.mark.asyncio
# async def test_update_avatar_url(user_repository, mock_session, user):
#     # Setup
#     new_avatar_url = "http://example.com/new_avatar.png"
#     mock_session.execute.return_value = AsyncMock(return_value=user)  # Use AsyncMock correctly
#
#     # Call method
#     result = await user_repository.update_avatar_url(email="test@example.com", url=new_avatar_url)
#
#     # Assertions
#     assert result.avatar == new_avatar_url
#     mock_session.commit.assert_awaited_once()
#     mock_session.refresh.assert_awaited_once_with(user)
#
#

#
# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.database.models import User
# from src.repository.users import UserRepository
# from schemas import UserCreate
#
#
# @pytest.fixture
# def mock_session():
#     return AsyncMock(spec=AsyncSession)
#
#
# @pytest.fixture
# def user_repository(mock_session):
#     return UserRepository(mock_session)
#
#
# @pytest.fixture
# def user():
#     return User(id=1, username="testuser", email="test@example.com", confirmed=False)
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_id(user_repository, mock_session, user):
#     # Setup mock
#     mock_result = AsyncMock()
#     mock_result.scalar_one_or_none.return_value = user  # Mock scalar_one_or_none properly
#     mock_session.execute.return_value = mock_result
#
#     # Call method
#     result = await user_repository.get_user_by_id(user_id=1)
#
#     # Assertions
#     assert result is not None
#     assert result.id == 1
#     assert result.username == "testuser"
#     assert result.email == "test@example.com"
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_username(user_repository, mock_session, user):
#     # Setup mock
#     mock_result = AsyncMock()
#     mock_result.scalar_one_or_none.return_value = user
#     mock_session.execute.return_value = mock_result
#
#     # Call method
#     result = await user_repository.get_user_by_username(username="testuser")
#
#     # Assertions
#     assert result is not None
#     assert result.username == "testuser"
#     assert result.email == "test@example.com"
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_email(user_repository, mock_session, user):
#     # Setup mock
#     mock_result = AsyncMock()
#     mock_result.scalar_one_or_none.return_value = user
#     mock_session.execute.return_value = mock_result
#
#     # Call method
#     result = await user_repository.get_user_by_email(email="test@example.com")
#
#     # Assertions
#     assert result is not None
#     assert result.email == "test@example.com"
#     assert result.username == "testuser"
#
#
# @pytest.mark.asyncio
# async def test_create_user(user_repository, mock_session):
#     # Setup
#     user_data = UserCreate(
#         username="newuser",
#         email="new@example.com",
#         password="securepassword"
#     )
#
#     # Call method
#     result = await user_repository.create_user(body=user_data, avatar="http://example.com/avatar.png")
#
#     # Assertions
#     assert isinstance(result, User)
#     assert result.username == "newuser"
#     assert result.email == "new@example.com"
#     assert result.avatar == "http://example.com/avatar.png"
#     mock_session.add.assert_called_once()
#     mock_session.commit.assert_awaited_once()
#     mock_session.refresh.assert_awaited_once_with(result)
#
#
# @pytest.mark.asyncio
# async def test_confirmed_email(user_repository, mock_session, user):
#     # Setup
#     user.confirmed = False
#
#     # Mock the async function execution
#     mock_session.execute.return_value = AsyncMock(return_value=user)  # Return an AsyncMock coroutine
#
#     # Call method
#     await user_repository.confirmed_email(email="test@example.com")
#
#     # Assertions
#     assert user.confirmed is True
#     mock_session.commit.assert_awaited_once()
#
#
# @pytest.mark.asyncio
# async def test_update_avatar_url(user_repository, mock_session, user):
#     # Setup
#     new_avatar_url = "http://example.com/new_avatar.png"
#     # Mock the async function execution and return the user object
#     mock_session.execute.return_value = AsyncMock(return_value=user)  # Return an AsyncMock coroutine
#
#     # Call method
#     result = await user_repository.update_avatar_url(email="test@example.com", url=new_avatar_url)
#
#     # Assertions
#     assert result.avatar == new_avatar_url
#     mock_session.commit.assert_awaited_once()
#     mock_session.refresh.assert_awaited_once_with(user)
