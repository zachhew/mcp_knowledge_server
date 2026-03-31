from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.models.document import Document
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.models.audit_log import AuditLog
from app.domain.models.note import Note
from app.domain.models.api_client import ApiClient


class ProjectRepositoryProtocol(Protocol):
    async def get_by_id(self, project_id: UUID) -> Project | None: ...
    async def get_by_slug(self, slug: str) -> Project | None: ...
    async def list_all(self) -> Sequence[Project]: ...


class DocumentRepositoryProtocol(Protocol):
    async def get_by_id(self, document_id: UUID) -> Document | None: ...
    async def list_by_project(self, project_id: UUID, limit: int = 20) -> Sequence[Document]: ...
    async def search(
        self,
        query: str,
        project_id: UUID | None = None,
        limit: int = 10,
    ) -> Sequence[Document]: ...


class TaskRepositoryProtocol(Protocol):
    async def get_by_id(self, task_id: UUID) -> Task | None: ...
    async def list_by_project(self, project_id: UUID, limit: int = 20) -> Sequence[Task]: ...
    async def search(
        self,
        query: str | None = None,
        project_id: UUID | None = None,
        assignee: str | None = None,
        limit: int = 20,
    ) -> Sequence[Task]: ...


class NoteRepositoryProtocol(Protocol):
    async def get_by_idempotency_key(self, idempotency_key: str) -> Note | None: ...
    async def create(self, note: Note) -> Note: ...


class TaskWriteRepositoryProtocol(Protocol):
    async def create(self, task: Task) -> Task: ...


class AuditLogRepositoryProtocol(Protocol):
    async def create(self, audit_log: AuditLog) -> AuditLog: ...


class ApiClientRepositoryProtocol(Protocol):
    async def get_by_name(self, name: str) -> ApiClient | None: ...
    async def get_by_hashed_api_key(self, hashed_api_key: str) -> ApiClient | None: ...