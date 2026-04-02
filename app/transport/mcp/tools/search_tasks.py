from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.task_service import TaskService
from app.infrastructure.repositories.task_repository import SQLAlchemyTaskRepository
from app.transport.mcp.context import ToolExecutionContext


class SearchTasksInput(BaseModel):
    query: str | None = None
    project_id: UUID | None = None
    assignee: str | None = None
    limit: int = Field(default=20, ge=1, le=50)


class SearchTasksItem(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    assignee: str | None
    created_by: str


class SearchTasksOutput(BaseModel):
    items: list[SearchTasksItem]


async def search_tasks_handler(
    execution_context: ToolExecutionContext,
    payload: SearchTasksInput,
) -> dict[str, Any]:
    session = execution_context.db_session

    repository = SQLAlchemyTaskRepository(session)
    service = TaskService(repository)

    tasks = await service.search_tasks(
        query=payload.query,
        project_id=payload.project_id,
        assignee=payload.assignee,
        limit=payload.limit,
    )

    return {
        "items": [
            {
                "id": item.id,
                "project_id": item.project_id,
                "title": item.title,
                "description": item.description,
                "status": item.status.value,
                "priority": item.priority.value,
                "assignee": item.assignee,
                "created_by": item.created_by,
            }
            for item in tasks
        ]
    }
