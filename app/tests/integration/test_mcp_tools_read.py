from __future__ import annotations

import pytest
from sqlalchemy import select

from app.domain.models.audit_log import AuditLog
from app.domain.models.note import Note
from app.domain.models.task import Task
from app.infrastructure.db.session import SessionFactory


async def test_create_task_creates_task_and_returns_payload(
    client, auth_headers, prepared_data
) -> None:
    response = await client.post(
        "/api/v1/mcp",
        headers=auth_headers,
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "create_task",
                "arguments": {
                    "project_id": prepared_data["project_id"],
                    "title": "Add MCP contract tests",
                    "description": "Cover tool contracts and payload validation.",
                    "priority": "high",
                    "assignee": "zach",
                    "created_by": "platform-team",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert payload["result"]["toolName"] == "create_task"
    assert payload["result"]["content"]["title"] == "Add MCP contract tests"


async def test_create_note_is_idempotent(client, auth_headers, prepared_data) -> None:
    request_payload = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "create_note",
            "arguments": {
                "project_id": prepared_data["project_id"],
                "author_type": "user",
                "author_id": "zach",
                "content": "Need stronger audit coverage.",
                "idempotency_key": "idem-note-001",
            },
        },
    }

    first_response = await client.post("/api/v1/mcp", headers=auth_headers, json=request_payload)
    second_response = await client.post("/api/v1/mcp", headers=auth_headers, json=request_payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_payload = first_response.json()
    second_payload = second_response.json()

    assert first_payload["error"] is None
    assert second_payload["error"] is None
    assert first_payload["result"]["content"]["id"] == second_payload["result"]["content"]["id"]


@pytest.mark.asyncio
async def test_create_note_writes_single_row_due_to_idempotency_async(
    client,
    auth_headers,
    prepared_data,
    db_session,
) -> None:
    request_payload = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "create_note",
            "arguments": {
                "project_id": prepared_data["project_id"],
                "author_type": "user",
                "author_id": "zach",
                "content": "Idempotency should prevent duplicates.",
                "idempotency_key": "idem-note-002",
            },
        },
    }

    await client.post("/api/v1/mcp", headers=auth_headers, json=request_payload)
    await client.post("/api/v1/mcp", headers=auth_headers, json=request_payload)

    result = await db_session.execute(select(Note).where(Note.idempotency_key == "idem-note-002"))
    assert len(result.scalars().all()) == 1


@pytest.mark.asyncio
async def test_search_knowledge_fts_returns_documents(client, auth_headers, prepared_data) -> None:
    response = await client.post(
        "/api/v1/mcp",
        headers=auth_headers,
        json={
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "search_knowledge",
                "arguments": {
                    "query": "retrieval tasks notes",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert len(payload["result"]["content"]["items"]) >= 1
