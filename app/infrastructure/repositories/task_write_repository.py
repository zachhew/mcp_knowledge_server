from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task import Task


class SQLAlchemyTaskWriteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, task: Task) -> Task:
        self._session.add(task)
        await self._session.flush()
        return task
