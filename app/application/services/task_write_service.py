from __future__ import annotations

from app.application.dto.tasks import TaskCreateDTO, TaskCreatedDTO
from app.application.interfaces.repositories import (
    AuditLogRepositoryProtocol,
    ProjectRepositoryProtocol,
    TaskWriteRepositoryProtocol,
)
from app.core.exceptions import NotFoundError, ValidationAppError
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.task_status import TaskStatus
from app.domain.models.audit_log import AuditLog
from app.domain.models.task import Task


class TaskWriteService:
    def __init__(
        self,
        task_repository: TaskWriteRepositoryProtocol,
        project_repository: ProjectRepositoryProtocol,
        audit_log_repository: AuditLogRepositoryProtocol,
    ) -> None:
        self._task_repository = task_repository
        self._project_repository = project_repository
        self._audit_log_repository = audit_log_repository

    async def create_task(self, payload: TaskCreateDTO) -> TaskCreatedDTO:
        project = await self._project_repository.get_by_id(payload.project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if not payload.title.strip():
            raise ValidationAppError("Task title must not be empty")

        task = Task(
            project_id=payload.project_id,
            title=payload.title,
            description=payload.description,
            status=TaskStatus.OPEN,
            priority=payload.priority,
            assignee=payload.assignee,
            created_by=payload.created_by,
        )
        created = await self._task_repository.create(task)

        audit_log = AuditLog(
            client_id=None,
            request_id=None,
            tool_name="create_task",
            action_type=AuditAction.TASK_CREATED,
            input_payload=payload.title,
            output_status="success",
            error_code=None,
        )
        await self._audit_log_repository.create(audit_log)

        return TaskCreatedDTO(
            id=created.id,
            project_id=created.project_id,
            title=created.title,
            description=created.description,
            status=created.status,
            priority=created.priority,
            assignee=created.assignee,
            created_by=created.created_by,
        )