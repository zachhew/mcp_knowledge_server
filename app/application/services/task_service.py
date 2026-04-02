from __future__ import annotations

from uuid import UUID

from app.application.dto.tasks import TaskListItemDTO
from app.application.interfaces.repositories import TaskRepositoryProtocol
from app.domain.models.task import Task


class TaskService:
    def __init__(self, repository: TaskRepositoryProtocol) -> None:
        self._repository = repository

    async def search_tasks(
        self,
        query: str | None = None,
        project_id: UUID | None = None,
        assignee: str | None = None,
        limit: int = 20,
    ) -> list[TaskListItemDTO]:
        tasks = await self._repository.search(
            query=query,
            project_id=project_id,
            assignee=assignee,
            limit=limit,
        )
        return [self._to_dto(task) for task in tasks]

    async def list_project_tasks(
        self,
        project_id: UUID,
        limit: int = 20,
    ) -> list[TaskListItemDTO]:
        tasks = await self._repository.list_by_project(project_id=project_id, limit=limit)
        return [self._to_dto(task) for task in tasks]

    @staticmethod
    def _to_dto(task: Task) -> TaskListItemDTO:
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
