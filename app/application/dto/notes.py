from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class NoteCreateDTO:
    project_id: UUID
    author_type: str
    author_id: str
    content: str
    idempotency_key: str | None = None


@dataclass(slots=True)
class NoteCreatedDTO:
    id: UUID
    project_id: UUID
    author_type: str
    author_id: str
    content: str
    idempotency_key: str | None
