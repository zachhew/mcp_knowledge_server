from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ToolExecutionResult(BaseModel):
    tool_name: str
    content: dict[str, Any]
    is_error: bool = False
    error_message: str | None = None
