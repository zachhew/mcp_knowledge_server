from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.domain.enums.document_type import DocumentType
from app.domain.enums.task_priority import TaskPriority
from app.domain.enums.task_status import TaskStatus
from app.domain.models.api_client import ApiClient
from app.domain.models.document import Document
from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.infrastructure.auth.api_key_auth import ApiKeyAuthService
from app.infrastructure.db.session import SessionFactory


async def seed() -> None:
    async with SessionFactory() as session:
        existing_project_result = await session.execute(
            select(Project).where(Project.slug == "aurora")
        )
        aurora_project = existing_project_result.scalar_one_or_none()

        if aurora_project is None:
            project = Project(
                slug="aurora",
                name="Aurora MCP Platform",
                description="Internal knowledge and actions platform for LLM-driven workflows.",
                owner="platform-team",
                tags="mcp,llm,knowledge,internal-tools",
            )
            session.add(project)
            await session.flush()

            architecture_doc = Document(
                project_id=project.id,
                title="Aurora Architecture Overview",
                content=(
                    "Aurora is a modular MCP knowledge server. "
                    "It provides tools for document retrieval, project context assembly, "
                    "task search, and safe write actions."
                ),
                summary="High-level architecture of the Aurora MCP platform.",
                owner="platform-team",
                tags="architecture,mcp,backend",
                document_type=DocumentType.SPEC,
            )

            runbook_doc = Document(
                project_id=project.id,
                title="Aurora Incident Runbook",
                content=(
                    "If retrieval latency increases, verify database health, inspect indexes, "
                    "check Redis connectivity, and inspect recent deploys."
                ),
                summary="Operational runbook for Aurora incidents.",
                owner="sre-team",
                tags="runbook,operations,incident",
                document_type=DocumentType.RUNBOOK,
            )

            session.add_all([architecture_doc, runbook_doc])
            await session.flush()

            chunks = [
                DocumentChunk(
                    document_id=architecture_doc.id,
                    chunk_index=0,
                    content="Aurora is a modular MCP knowledge server.",
                    token_count=8,
                ),
                DocumentChunk(
                    document_id=architecture_doc.id,
                    chunk_index=1,
                    content="It supports retrieval, context assembly, and safe actions.",
                    token_count=9,
                ),
                DocumentChunk(
                    document_id=runbook_doc.id,
                    chunk_index=0,
                    content="Check database health and indexes during latency incidents.",
                    token_count=9,
                ),
            ]
            session.add_all(chunks)

            tasks = [
                Task(
                    project_id=project.id,
                    title="Add document filtering by tags",
                    description="Support metadata filtering in search_knowledge.",
                    status=TaskStatus.OPEN,
                    priority=TaskPriority.HIGH,
                    assignee="zach",
                    created_by="platform-team",
                ),
                Task(
                    project_id=project.id,
                    title="Instrument repository metrics",
                    description="Track query latency and result counts for search operations.",
                    status=TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.MEDIUM,
                    assignee="observability-team",
                    created_by="platform-team",
                ),
            ]
            session.add_all(tasks)

        existing_client_result = await session.execute(
            select(ApiClient).where(ApiClient.name == "local-dev-client")
        )
        local_client = existing_client_result.scalar_one_or_none()

        if local_client is None:
            api_client = ApiClient(
                name="local-dev-client",
                hashed_api_key=ApiKeyAuthService.hash_api_key("dev-secret-key"),
                scopes="knowledge:read,projects:read,tasks:read,tasks:write,notes:write",
                is_active=True,
            )
            session.add(api_client)

        await session.commit()
        print("Seed completed.")


if __name__ == "__main__":
    asyncio.run(seed())