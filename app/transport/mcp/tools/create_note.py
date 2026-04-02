from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.application.dto.notes import NoteCreateDTO
from app.application.services.note_service import NoteService
from app.infrastructure.repositories.audit_log_repository import SQLAlchemyAuditLogRepository
from app.infrastructure.repositories.note_repository import SQLAlchemyNoteRepository
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.transport.mcp.context import ToolExecutionContext


class CreateNoteInput(BaseModel):
    project_id: UUID
    author_type: str = Field(..., min_length=1)
    author_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    idempotency_key: str | None = None


class CreateNoteOutput(BaseModel):
    id: UUID
    project_id: UUID
    author_type: str
    author_id: str
    content: str
    idempotency_key: str | None


async def create_note_handler(
    execution_context: ToolExecutionContext,
    payload: CreateNoteInput,
) -> dict[str, Any]:
    session = execution_context.db_session

    note_repository = SQLAlchemyNoteRepository(session)
    project_repository = SQLAlchemyProjectRepository(session)
    audit_log_repository = SQLAlchemyAuditLogRepository(session)

    service = NoteService(
        note_repository=note_repository,
        project_repository=project_repository,
        audit_log_repository=audit_log_repository,
    )

    created = await service.create_note(
        NoteCreateDTO(
            project_id=payload.project_id,
            author_type=payload.author_type,
            author_id=payload.author_id,
            content=payload.content,
            idempotency_key=payload.idempotency_key,
        ),
        request_context=execution_context.request_context,
    )

    await session.commit()

    return {
        "id": created.id,
        "project_id": created.project_id,
        "author_type": created.author_type,
        "author_id": created.author_id,
        "content": created.content,
        "idempotency_key": created.idempotency_key,
    }
