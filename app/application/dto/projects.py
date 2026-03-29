from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.application.dto.documents import DocumentListItemDTO
from app.application.dto.tasks import TaskListItemDTO


@dataclass(slots=True)
class ProjectDTO:
    id: UUID
    slug: str
    name: str
    description: str | None
    owner: str
    tags: str | None


@dataclass(slots=True)
class ProjectContextDTO:
    project: ProjectDTO
    recent_documents: list[DocumentListItemDTO]
    open_tasks: list[TaskListItemDTO]