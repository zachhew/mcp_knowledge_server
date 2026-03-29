from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str | None = None
    method: str = Field(..., min_length=1)
    params: dict[str, Any] | None = None


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: dict[str, Any] | None = None


class JsonRpcResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str | None = None
    result: dict[str, Any] | None = None
    error: JsonRpcError | None = None


class ToolCallParams(BaseModel):
    name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)