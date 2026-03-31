from __future__ import annotations


async def test_tools_list_contract_shape(client, auth_headers, prepared_data) -> None:
    response = await client.post(
        "/api/v1/mcp",
        headers=auth_headers,
        json={
            "jsonrpc": "2.0",
            "id": "contract-1",
            "method": "tools/list",
            "params": {},
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == "contract-1"
    assert payload["error"] is None
    assert "tools" in payload["result"]

    tools = payload["result"]["tools"]
    assert isinstance(tools, list)
    assert len(tools) >= 1

    first_tool = tools[0]
    assert "name" in first_tool
    assert "description" in first_tool
    assert "requiredScope" in first_tool
    assert "inputSchema" in first_tool
    assert "outputSchema" in first_tool