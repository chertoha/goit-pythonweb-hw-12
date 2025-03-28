import pytest
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import Hash, create_access_token, get_current_user, create_email_token, get_email_from_token
from fastapi import HTTPException
from jose import JWTError
from unittest.mock import AsyncMock, patch
from src.services.users import UserService


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def password_hash():
    hash_util = Hash()
    return hash_util.get_password_hash("12345678")


@pytest.mark.asyncio
async def test_create_access_token():
    data = {"sub": "testuser"}
    token = await create_access_token(data=data)

    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_create_access_token_with_expiration():
    data = {"sub": "testuser"}
    expiration_time = 60
    token = await create_access_token(data=data, expires_delta=expiration_time)

    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_create_email_token():
    email_data = {"sub": "test@example.com"}
    token = create_email_token(data=email_data)

    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_get_email_from_token():
    email_data = {"sub": "test@example.com"}
    token = create_email_token(data=email_data)

    email = await get_email_from_token(token=token)
    assert email == "test@example.com"


@pytest.mark.asyncio
async def test_get_email_from_token_invalid():
    invalid_token = "invalid.token.string"

    with pytest.raises(HTTPException):
        await get_email_from_token(token=invalid_token)


def test_verify_password(password_hash):
    hash_util = Hash()

    assert hash_util.verify_password("12345678", password_hash)

    assert not hash_util.verify_password("wrongpassword", password_hash)



@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
    invalid_token = "invalid.token.string"

    with pytest.raises(HTTPException):
        await get_current_user(token=invalid_token, db=mock_db)



@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_db):
    token = await create_access_token(data={"sub": "nonexistentuser"})

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    with patch.object(UserService, "get_user_by_username", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = None

        with pytest.raises(HTTPException):
            await get_current_user(token=token, db=mock_db, redis=mock_redis)