from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import RequestContext


@dataclass(slots=True, frozen=True)
class ToolExecutionContext:
    db_session: AsyncSession
    request_context: RequestContext