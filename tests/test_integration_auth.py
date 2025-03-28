
import pytest
from sqlalchemy import select

from src.conf.config import settings
from src.database.models import User
from src.services.users import UserService
from tests.conftest import TestingSessionLocal
from jose import jwt
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from datetime import datetime, timedelta, UTC

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678", "role":"ADMIN"}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"

def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_wrong_username_login(client):
    response = client.post("api/auth/login",
                           data={"username": "username", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data



@pytest.mark.asyncio
async def test_request_email_confirmed(client):
    email_data = {"email": "agent007@gmail.com"}


    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.email == email_data["email"]))
        user = user.scalar_one_or_none()
        if user:
            user.confirmed = True
            await session.commit()

    response = client.post("api/auth/request_email", json=email_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Ваша електронна пошта вже підтверджена"



# -----------------------------------------------------------------------------
#
#
@pytest.mark.asyncio
async def test_refresh_token_valid(client):
    """
    Tests the refresh endpoint with a valid refresh token.
    """
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.email == user_data.get("email")))
        user = user.scalar_one_or_none()
        if user:
            user.confirmed = True
            await session.commit()

    refresh_token_data = {"sub": user_data["username"], "token_type": "refresh"}
    refresh_token = jwt.encode(refresh_token_data, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM)

    with patch("src.services.auth.verify_refresh_token", new_callable=AsyncMock) as mock_verify_refresh_token:
        mock_verify_refresh_token.return_value = MagicMock(username=user_data["username"], id=1)

        with patch.object(UserService, "get_user_by_username", new_callable=AsyncMock) as mock_get_user_by_username:
            mock_get_user_by_username.return_value = MagicMock(
                username=user_data["username"],
                id=1,
                refresh_token=refresh_token
            )

            response = client.post(
                "api/auth/refresh",
                headers={"Authorization": f"Bearer {refresh_token}"},
            )


    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"



@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    """
    Tests the refresh endpoint with an invalid refresh token.
    """
    with patch("src.services.auth.verify_refresh_token", new_callable=AsyncMock) as mock_verify_refresh_token:
        mock_verify_refresh_token.return_value = MagicMock(username=user_data["username"], id=1)

        with patch.object(UserService, "get_user_by_username", new_callable=AsyncMock) as mock_get_user_by_username:
            mock_get_user_by_username.return_value = None

            response = client.post(
                "api/auth/refresh",
                headers={"Authorization": "Bearer invalid_token"},
            )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Невалідний або прострочений refresh token"



@pytest.mark.asyncio
async def test_refresh_token_expired(client):
    """
    Tests the refresh endpoint with an expired refresh token.
    """
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.email == user_data.get("email")))
        user = user.scalar_one_or_none()
        if user:
            user.confirmed = True
            await session.commit()

    expired_token_data = {
        "sub": user_data["username"],
        "exp": datetime.now(UTC) - timedelta(seconds=1),
        "token_type": "refresh",
    }
    expired_token = jwt.encode(
        expired_token_data, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    with patch("src.services.auth.verify_refresh_token", new_callable=AsyncMock) as mock_verify_refresh_token:
        mock_verify_refresh_token.return_value = MagicMock(username=user_data["username"], id=1)

        with patch.object(UserService, "get_user_by_username", new_callable=AsyncMock) as mock_get_user_by_username:
            mock_get_user_by_username.return_value = None

            response = client.post(
                "api/auth/refresh",
                headers={"Authorization": f"Bearer {expired_token}"},
            )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Невалідний або прострочений refresh token"
