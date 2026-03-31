from __future__ import annotations

import uuid

import pytest

from app.core.exceptions import ValidationAppError
from app.core.request_context import RequestContext
from app.transport.mcp.auth import require_scope


def test_require_scope_accepts_present_scope() -> None:
    context = RequestContext(
        request_id="req-1",
        client_id=uuid.uuid4(),
        client_name="test-client",
        scopes=frozenset({"knowledge:read", "tasks:write"}),
    )

    require_scope(context, "knowledge:read")


def test_require_scope_rejects_missing_scope() -> None:
    context = RequestContext(
        request_id="req-1",
        client_id=uuid.uuid4(),
        client_name="test-client",
        scopes=frozenset({"knowledge:read"}),
    )

    with pytest.raises(ValidationAppError):
        require_scope(context, "tasks:write")