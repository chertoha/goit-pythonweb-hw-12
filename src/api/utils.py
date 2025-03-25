"""
Utility API module for health checks and diagnostics.

This module contains the `utils` router, which provides endpoints for system health checks,
such as checking the database connection.

Endpoints:
    - GET /healthchecker: Performs a simple health check to verify that the database is connected.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
        Performs a health check by verifying that the database is correctly configured.

        Args:
            db (AsyncSession): The database session.

        Returns:
            dict: A success message if the database is connected, or an error if not.
    """
    try:
        # Виконуємо асинхронний запит
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
