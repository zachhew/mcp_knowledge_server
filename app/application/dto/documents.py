from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.enums.document_type import DocumentType


@dataclass(slots=True)
class DocumentListItemDTO:
    id: UUID
    project_id: UUID
    title: str
    summary: str | None
    owner: str
    document_type: DocumentType
    tags: str | None