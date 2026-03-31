from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.document_service import DocumentService
from app.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from app.transport.mcp.context import ToolExecutionContext


class SearchKnowledgeInput(BaseModel):
    query: str = Field(..., min_length=1)
    project_id: UUID | None = None
    limit: int = Field(default=10, ge=1, le=50)


class SearchKnowledgeItem(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    summary: str | None
    owner: str
    document_type: str
    tags: str | None


class SearchKnowledgeOutput(BaseModel):
    items: list[SearchKnowledgeItem]


async def search_knowledge_handler(
    execution_context: ToolExecutionContext,
    payload: SearchKnowledgeInput,
) -> dict[str, Any]:
    session = execution_context.db_session

    repository = SQLAlchemyDocumentRepository(session)
    service = DocumentService(repository)

    documents = await service.search_documents(
        query=payload.query,
        project_id=payload.project_id,
        limit=payload.limit,
    )

    return {
        "items": [
            {
                "id": item.id,
                "project_id": item.project_id,
                "title": item.title,
                "summary": item.summary,
                "owner": item.owner,
                "document_type": item.document_type.value,
                "tags": item.tags,
            }
            for item in documents
        ]
    }