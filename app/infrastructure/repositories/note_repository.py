from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.note import Note


class SQLAlchemyNoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_idempotency_key(self, idempotency_key: str) -> Note | None:
        stmt = select(Note).where(Note.idempotency_key == idempotency_key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, note: Note) -> Note:
        self._session.add(note)
        await self._session.flush()
        return note