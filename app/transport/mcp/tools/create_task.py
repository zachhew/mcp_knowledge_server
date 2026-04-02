from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.tasks import TaskCreateDTO
from app.application.services.task_write_service import TaskWriteService
from app.domain.enums.task_priority import TaskPriority
from app.infrastructure.repositories.audit_log_repository import SQLAlchemyAuditLogRepository
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.infrastructure.repositories.task_write_repository import SQLAlchemyTaskWriteRepository
from app.transport.mcp.context import ToolExecutionContext


class CreateTaskInput(BaseModel):
    project_id: UUID
    title: str = Field(..., min_length=1)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: str | None = None
    created_by: str = Field(..., min_length=1)


class CreateTaskOutput(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    assignee: str | None
    created_by: str


async def create_task_handler(
    execution_context: ToolExecutionContext,
    payload: CreateTaskInput,
) -> dict[str, Any]:
    session = execution_context.db_session

    task_repository = SQLAlchemyTaskWriteRepository(session)
    project_repository = SQLAlchemyProjectRepository(session)
    audit_log_repository = SQLAlchemyAuditLogRepository(session)

    service = TaskWriteService(
        task_repository=task_repository,
        project_repository=project_repository,
        audit_log_repository=audit_log_repository,
    )

    created = await service.create_task(
        TaskCreateDTO(
            project_id=payload.project_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            assignee=payload.assignee,
            created_by=payload.created_by,
        ),
        request_context=execution_context.request_context,
    )

    await session.commit()

    return {
        "id": created.id,
        "project_id": created.project_id,
        "title": created.title,
        "description": created.description,
        "status": created.status.value,
        "priority": created.priority.value,
        "assignee": created.assignee,
        "created_by": created.created_by,
    }
