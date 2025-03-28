import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from schemas import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com", confirmed=False, role="ADMIN")


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_id(user_id=1)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_username(username="testuser")

    # Assertions
    assert result is not None
    assert result.username == "testuser"
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_email(email="test@example.com")

    # Assertions
    assert result is not None
    assert result.email == "test@example.com"
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    # Setup
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="securepassword",
        role="ADMIN"
    )

    # Call method
    result = await user_repository.create_user(body=user_data, avatar="http://example.com/avatar.png")

    # Assertions
    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "new@example.com"
    assert result.avatar == "http://example.com/avatar.png"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_confirmed_email():
    mock_session = AsyncMock()
    repo = UserRepository(mock_session)

    mock_user = User(email="test@example.com", confirmed=False, role="ADMIN")
    repo.get_user_by_email = AsyncMock(return_value=mock_user)

    await repo.confirmed_email("test@example.com")

    assert mock_user.confirmed is True
    mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_avatar_url():
    mock_session = AsyncMock()
    repo = UserRepository(mock_session)

    mock_user = User(email="test@example.com", avatar="old_url", role="ADMIN")
    repo.get_user_by_email = AsyncMock(return_value=mock_user)

    updated_user = await repo.update_avatar_url("test@example.com", "new_url")

    assert updated_user.avatar == "new_url"
    mock_session.commit.assert_awaited()
    mock_session.refresh.assert_awaited_with(mock_user)