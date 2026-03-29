from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.document import Document


class SQLAlchemyDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, document_id: UUID) -> Document | None:
        stmt = select(Document).where(Document.id == document_id, Document.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: UUID, limit: int = 20) -> Sequence[Document]:
        stmt = (
            select(Document)
            .where(Document.project_id == project_id, Document.is_deleted.is_(False))
            .order_by(Document.updated_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def search(
        self,
        query: str,
        project_id: UUID | None = None,
        limit: int = 10,
    ) -> Sequence[Document]:
        stmt = select(Document).where(Document.is_deleted.is_(False))

        if project_id is not None:
            stmt = stmt.where(Document.project_id == project_id)

        pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                Document.title.ilike(pattern),
                Document.content.ilike(pattern),
                Document.summary.ilike(pattern),
                Document.tags.ilike(pattern),
            )
        ).order_by(Document.updated_at.desc()).limit(limit)

        result = await self._session.execute(stmt)
        return result.scalars().all()