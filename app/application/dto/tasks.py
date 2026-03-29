from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.enums.task_priority import TaskPriority
from app.domain.enums.task_status import TaskStatus


@dataclass(slots=True)
class TaskListItemDTO:
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee: str | None
    created_by: str


@dataclass(slots=True)
class TaskCreateDTO:
    project_id: UUID
    title: str
    description: str | None
    priority: TaskPriority
    assignee: str | None
    created_by: str


@dataclass(slots=True)
class TaskCreatedDTO:
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee: str | None
    created_by: str