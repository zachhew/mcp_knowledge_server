import hashlib

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.document_type import DocumentType
from app.domain.enums.task_priority import TaskPriority
from app.domain.enums.task_status import TaskStatus
from app.domain.models.api_client import ApiClient
from app.domain.models.audit_log import AuditLog
from app.domain.models.document import Document
from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.note import Note
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.infrastructure.db.session import SessionFactory
from app.main import app
from app.infrastructure.db.session import engine


TEST_API_KEY = "test-secret-key"
TEST_API_KEY_HASH = hashlib.sha256(TEST_API_KEY.encode("utf-8")).hexdigest()


@pytest_asyncio.fixture(autouse=True)
async def reset_engine_pool():
    await engine.dispose()
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with SessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def prepared_data(db_session: AsyncSession) -> dict[str, str]:
    await db_session.execute(delete(AuditLog))
    await db_session.execute(delete(Note))
    await db_session.execute(delete(DocumentChunk))
    await db_session.execute(delete(Document))
    await db_session.execute(delete(Task))
    await db_session.execute(delete(ApiClient))
    await db_session.execute(delete(Project))
    await db_session.commit()

    project = Project(
        slug="aurora-test",
        name="Aurora Test Platform",
        description="Test project for MCP integration tests.",
        owner="platform-team",
        tags="mcp,llm,test",
    )
    db_session.add(project)
    await db_session.flush()

    document = Document(
        project_id=project.id,
        title="Aurora Test Architecture",
        content="Aurora test architecture includes retrieval, tasks, and notes.",
        summary="Test architecture summary.",
        owner="platform-team",
        tags="architecture,test",
        document_type=DocumentType.SPEC,
    )
    db_session.add(document)
    await db_session.flush()

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="Aurora test architecture includes retrieval.",
        token_count=6,
    )
    db_session.add(chunk)

    task = Task(
        project_id=project.id,
        title="Add structured audit payload",
        description="Improve audit payload shape.",
        status=TaskStatus.OPEN,
        priority=TaskPriority.HIGH,
        assignee="zach",
        created_by="platform-team",
    )
    db_session.add(task)

    api_client = ApiClient(
        name="test-client",
        hashed_api_key=TEST_API_KEY_HASH,
        scopes="knowledge:read,projects:read,tasks:read,tasks:write,notes:write",
        is_active=True,
    )
    db_session.add(api_client)

    await db_session.commit()

    return {
        "project_id": str(project.id),
        "document_id": str(document.id),
        "api_key": TEST_API_KEY,
    }


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "x-api-key": TEST_API_KEY,
        "x-request-id": "test-request-001",
    }
