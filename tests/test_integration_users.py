from io import BytesIO

from src.database.models import UserRole
from tests.conftest import get_token
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.database.models import User
import src.database.redis as redis_module

user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
    "role":"ADMIN",
    "confirmed": True
}

@pytest.mark.asyncio
async def test_get_user_profile(client, monkeypatch, get_token):

    response = client.get(
        "api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["username"] == "deadpool"


def test_update_user_avatar(client, get_token):
    image_content = b"fake_image_data"
    image_file = BytesIO(image_content)
    image_file.name = "avatar.jpg"

    mock_avatar_url = "https://fake-cloudinary-url.com/avatar.jpg"


    with patch("src.services.upload_file.UploadFileService.upload_file", return_value=mock_avatar_url):
        with patch.object(redis_module.r, "Redis", new_callable=AsyncMock) as mock_redis:
            mock_redis_instance = mock_redis.return_value
            mock_redis_instance.get.return_value = None

            with patch("src.services.auth.get_current_user") as mock_get_current_user:

                mock_user = User(id=1, username="testuser", email="test@example.com", confirmed=False, role="ADMIN")

                mock_get_current_user.return_value = mock_user

                response = client.patch(
                    "api/users/avatar",
                    files={"file": image_file},
                    headers={"Authorization": f"Bearer {get_token}"}
                )



    data = response.json()
    assert response.status_code == 200
    assert data["username"] == "deadpool"
    assert data["avatar"] == mock_avatar_url

