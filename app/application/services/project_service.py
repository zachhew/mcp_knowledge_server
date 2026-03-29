from __future__ import annotations

from uuid import UUID

from app.application.dto.documents import DocumentListItemDTO
from app.application.dto.projects import ProjectContextDTO, ProjectDTO
from app.application.dto.tasks import TaskListItemDTO
from app.application.interfaces.repositories import (
    DocumentRepositoryProtocol,
    ProjectRepositoryProtocol,
    TaskRepositoryProtocol,
)
from app.domain.models.document import Document
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.enums.task_status import TaskStatus


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepositoryProtocol,
        document_repository: DocumentRepositoryProtocol,
        task_repository: TaskRepositoryProtocol,
    ) -> None:
        self._project_repository = project_repository
        self._document_repository = document_repository
        self._task_repository = task_repository

    async def get_project_by_slug(self, slug: str) -> ProjectDTO | None:
        project = await self._project_repository.get_by_slug(slug)
        if project is None:
            return None

        return self._to_project_dto(project)

    async def build_project_context(
        self,
        slug: str,
        documents_limit: int = 5,
        tasks_limit: int = 10,
    ) -> ProjectContextDTO | None:
        project = await self._project_repository.get_by_slug(slug)
        if project is None:
            return None

        documents = await self._document_repository.list_by_project(
            project_id=project.id,
            limit=documents_limit,
        )
        tasks = await self._task_repository.list_by_project(
            project_id=project.id,
            limit=tasks_limit,
        )

        open_tasks = [task for task in tasks if task.status != TaskStatus.DONE]

        return ProjectContextDTO(
            project=self._to_project_dto(project),
            recent_documents=[self._to_document_dto(document) for document in documents],
            open_tasks=[self._to_task_dto(task) for task in open_tasks],
        )

    @staticmethod
    def _to_project_dto(project: Project) -> ProjectDTO:
        return ProjectDTO(
            id=project.id,
            slug=project.slug,
            name=project.name,
            description=project.description,
            owner=project.owner,
            tags=project.tags,
        )

    @staticmethod
    def _to_document_dto(document: Document) -> DocumentListItemDTO:
        return DocumentListItemDTO(
            id=document.id,
            project_id=document.project_id,
            title=document.title,
            summary=document.summary,
            owner=document.owner,
            document_type=document.document_type,
            tags=document.tags,
        )

    @staticmethod
    def _to_task_dto(task: Task) -> TaskListItemDTO:
        return TaskListItemDTO(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assignee=task.assignee,
            created_by=task.created_by,
        )