from __future__ import annotations

from app.application.dto.notes import NoteCreateDTO, NoteCreatedDTO
from app.application.interfaces.repositories import (
    AuditLogRepositoryProtocol,
    NoteRepositoryProtocol,
    ProjectRepositoryProtocol,
)
from app.core.exceptions import NotFoundError
from app.core.request_context import RequestContext
from app.domain.enums.audit_action import AuditAction
from app.domain.models.audit_log import AuditLog
from app.domain.models.note import Note


class NoteService:
    def __init__(
        self,
        note_repository: NoteRepositoryProtocol,
        project_repository: ProjectRepositoryProtocol,
        audit_log_repository: AuditLogRepositoryProtocol,
    ) -> None:
        self._note_repository = note_repository
        self._project_repository = project_repository
        self._audit_log_repository = audit_log_repository

    async def create_note(
        self,
        payload: NoteCreateDTO,
        request_context: RequestContext,
    ) -> NoteCreatedDTO:
        project = await self._project_repository.get_by_id(payload.project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if payload.idempotency_key:
            existing = await self._note_repository.get_by_idempotency_key(payload.idempotency_key)
            if existing is not None:
                return NoteCreatedDTO(
                    id=existing.id,
                    project_id=existing.project_id,
                    author_type=existing.author_type,
                    author_id=existing.author_id,
                    content=existing.content,
                    idempotency_key=existing.idempotency_key,
                )

        note = Note(
            project_id=payload.project_id,
            author_type=payload.author_type,
            author_id=payload.author_id,
            content=payload.content,
            idempotency_key=payload.idempotency_key,
        )
        created = await self._note_repository.create(note)

        audit_log = AuditLog(
            client_id=request_context.client_id,
            request_id=request_context.request_id,
            tool_name="create_note",
            action_type=AuditAction.NOTE_CREATED,
            input_payload=payload.content,
            output_status="success",
            error_code=None,
        )
        await self._audit_log_repository.create(audit_log)

        return NoteCreatedDTO(
            id=created.id,
            project_id=created.project_id,
            author_type=created.author_type,
            author_id=created.author_id,
            content=created.content,
            idempotency_key=created.idempotency_key,
        )