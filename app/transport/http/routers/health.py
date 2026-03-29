from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_probe(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc

    return {"status": "ready"}