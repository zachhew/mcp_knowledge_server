from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.audit_log import AuditLog


class SQLAlchemyAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        self._session.add(audit_log)
        await self._session.flush()
        return audit_log
