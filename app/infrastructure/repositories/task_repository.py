from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task import Task


class SQLAlchemyTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, task_id: UUID) -> Task | None:
        stmt = select(Task).where(Task.id == task_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: UUID, limit: int = 20) -> Sequence[Task]:
        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def search(
        self,
        query: str | None = None,
        project_id: UUID | None = None,
        assignee: str | None = None,
        limit: int = 20,
    ) -> Sequence[Task]:
        stmt = select(Task)

        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)

        if assignee is not None:
            stmt = stmt.where(Task.assignee == assignee)

        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Task.title.ilike(pattern),
                    Task.description.ilike(pattern),
                )
            )

        stmt = stmt.order_by(Task.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()