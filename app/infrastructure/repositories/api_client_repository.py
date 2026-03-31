from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.api_client import ApiClient


class SQLAlchemyApiClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_name(self, name: str) -> ApiClient | None:
        stmt = select(ApiClient).where(ApiClient.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hashed_api_key(self, hashed_api_key: str) -> ApiClient | None:
        stmt = select(ApiClient).where(ApiClient.hashed_api_key == hashed_api_key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()