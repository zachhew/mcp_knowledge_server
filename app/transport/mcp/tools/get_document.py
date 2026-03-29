from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.document_service import DocumentService
from app.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository


class GetDocumentInput(BaseModel):
    document_id: UUID


class GetDocumentOutput(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    content: str
    summary: str | None
    owner: str
    document_type: str
    tags: str | None


async def get_document_handler(
    session: AsyncSession,
    payload: GetDocumentInput,
) -> dict[str, Any]:
    repository = SQLAlchemyDocumentRepository(session)
    service = DocumentService(repository)

    document = await service.get_document(payload.document_id)
    if document is None:
        raise ValueError("Document not found")

    return {
        "id": document.id,
        "project_id": document.project_id,
        "title": document.title,
        "content": document.content,
        "summary": document.summary,
        "owner": document.owner,
        "document_type": document.document_type.value,
        "tags": document.tags,
    }