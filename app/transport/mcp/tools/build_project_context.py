from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.project_service import ProjectService
from app.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.infrastructure.repositories.task_repository import SQLAlchemyTaskRepository


class BuildProjectContextInput(BaseModel):
    slug: str = Field(..., min_length=1)
    documents_limit: int = Field(default=5, ge=1, le=20)
    tasks_limit: int = Field(default=10, ge=1, le=50)


class ProjectContextProject(BaseModel):
    id: str
    slug: str
    name: str
    description: str | None
    owner: str
    tags: str | None


class ProjectContextDocument(BaseModel):
    id: str
    title: str
    summary: str | None
    owner: str
    document_type: str
    tags: str | None


class ProjectContextTask(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    assignee: str | None
    created_by: str


class BuildProjectContextOutput(BaseModel):
    project: ProjectContextProject
    recent_documents: list[ProjectContextDocument]
    open_tasks: list[ProjectContextTask]


async def build_project_context_handler(
    session: AsyncSession,
    payload: BuildProjectContextInput,
) -> dict[str, Any]:
    project_repository = SQLAlchemyProjectRepository(session)
    document_repository = SQLAlchemyDocumentRepository(session)
    task_repository = SQLAlchemyTaskRepository(session)

    service = ProjectService(
        project_repository=project_repository,
        document_repository=document_repository,
        task_repository=task_repository,
    )

    context = await service.build_project_context(
        slug=payload.slug,
        documents_limit=payload.documents_limit,
        tasks_limit=payload.tasks_limit,
    )
    if context is None:
        raise ValueError("Project not found")

    return {
        "project": {
            "id": str(context.project.id),
            "slug": context.project.slug,
            "name": context.project.name,
            "description": context.project.description,
            "owner": context.project.owner,
            "tags": context.project.tags,
        },
        "recent_documents": [
            {
                "id": str(item.id),
                "title": item.title,
                "summary": item.summary,
                "owner": item.owner,
                "document_type": str(item.document_type),
                "tags": item.tags,
            }
            for item in context.recent_documents
        ],
        "open_tasks": [
            {
                "id": str(item.id),
                "title": item.title,
                "description": item.description,
                "status": item.status.value,
                "priority": item.priority.value,
                "assignee": item.assignee,
                "created_by": item.created_by,
            }
            for item in context.open_tasks
        ],
    }