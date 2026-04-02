from __future__ import annotations


async def test_tools_list_requires_auth(client) -> None:
    response = await client.post(
        "/api/v1/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        },
    )

    assert response.status_code == 401


async def test_tools_list_returns_registered_tools(client, auth_headers, prepared_data) -> None:
    response = await client.post(
        "/api/v1/mcp",
        headers=auth_headers,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None

    tool_names = {tool["name"] for tool in payload["result"]["tools"]}
    assert "search_knowledge" in tool_names
    assert "build_project_context" in tool_names
    assert "create_task" in tool_names
    assert "create_note" in tool_names


async def test_search_knowledge_returns_documents(client, auth_headers, prepared_data) -> None:
    response = await client.post(
        "/api/v1/mcp",
        headers=auth_headers,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_knowledge",
                "arguments": {
                    "query": "Aurora",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert payload["result"]["toolName"] == "search_knowledge"
    assert len(payload["result"]["content"]["items"]) >= 1


async def test_build_project_context_returns_project_bundle(
    client, auth_headers, prepared_data
) -> None:
    response = await client.post(
        "/api/v1/mcp",
        headers=auth_headers,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "build_project_context",
                "arguments": {
                    "slug": "aurora-test",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert payload["result"]["toolName"] == "build_project_context"
    assert payload["result"]["content"]["project"]["slug"] == "aurora-test"
