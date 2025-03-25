from io import BytesIO
from tests.conftest import get_token
import pytest
from unittest.mock import patch

user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
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
        response = client.patch(
            "api/users/avatar",
            files={"file": image_file},
            headers={"Authorization": f"Bearer {get_token}"}
        )
    data = response.json()
    assert response.status_code == 200
    assert data["username"] == "deadpool"
    assert data["avatar"] == mock_avatar_url

