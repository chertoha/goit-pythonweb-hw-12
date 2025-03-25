
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_healthchecker_success(client):
    response = client.get("api/healthchecker")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to FastAPI!"}


@pytest.mark.asyncio
async def test_healthchecker_db_not_configured(client, monkeypatch):

    async def mock_execute(_):
        return AsyncMock(scalar_one_or_none=AsyncMock(return_value=None))

    monkeypatch.setattr(AsyncSession, "execute", mock_execute)

    response = client.get("api/healthchecker")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Error connecting to the database"}


@pytest.mark.asyncio
async def test_healthchecker_db_connection_error(client, monkeypatch):
    async def mock_execute(_):
        raise Exception("Database connection failed")

    monkeypatch.setattr(AsyncSession, "execute", mock_execute)

    response = client.get("api/healthchecker")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Error connecting to the database"}