from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.transport.mcp.context import ToolExecutionContext


ToolHandler = Callable[[ToolExecutionContext, BaseModel], Awaitable[dict[str, Any]]]


@dataclass(slots=True)
class RegisteredTool:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    required_scope: str
    handler: ToolHandler

    def to_definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "requiredScope": self.required_scope,
            "inputSchema": self.input_model.model_json_schema(),
            "outputSchema": self.output_model.model_json_schema(),
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        *,
        name: str,
        description: str,
        input_model: type[BaseModel],
        output_model: type[BaseModel],
        required_scope: str,
        handler: ToolHandler,
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool {name!r} is already registered")

        self._tools[name] = RegisteredTool(
            name=name,
            description=description,
            input_model=input_model,
            output_model=output_model,
            required_scope=required_scope,
            handler=handler,
        )

    def get(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {name}") from exc

    def list_definitions(self) -> list[dict[str, Any]]:
        return [tool.to_definition() for tool in self._tools.values()]
