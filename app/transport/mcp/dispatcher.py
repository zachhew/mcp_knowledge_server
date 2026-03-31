from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError

from app.core.exceptions import AppError
from app.transport.mcp.auth import require_scope
from app.transport.mcp.context import ToolExecutionContext
from app.transport.mcp.registry import ToolRegistry
from app.transport.mcp.result import ToolExecutionResult

logger = logging.getLogger(__name__)


class MCPDispatcher:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def list_tools(self) -> list[dict[str, Any]]:
        return self._registry.list_definitions()

    async def call_tool(
        self,
        execution_context: ToolExecutionContext,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolExecutionResult:
        logger.info(
            "Calling MCP tool: %s",
            tool_name,
            extra={
                "request_id": execution_context.request_context.request_id,
                "client_name": execution_context.request_context.client_name,
            },
        )

        session = execution_context.db_session

        try:
            tool = self._registry.get(tool_name)
            require_scope(execution_context.request_context, tool.required_scope)

            parsed_input = tool.input_model(**arguments)
            raw_result = await tool.handler(execution_context, parsed_input)
            parsed_output = tool.output_model(**raw_result)

            return ToolExecutionResult(
                tool_name=tool_name,
                content=parsed_output.model_dump(mode="json"),
                is_error=False,
                error_message=None,
            )

        except ValidationError as exc:
            logger.warning("Tool validation failed for %s: %s", tool_name, exc)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )

        except AppError as exc:
            logger.warning("Application error for %s: %s", tool_name, exc)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )

        except ValueError as exc:
            logger.warning("Tool execution rejected for %s: %s", tool_name, exc)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )

        except Exception as exc:
            logger.exception("Unhandled tool execution error for %s", tool_name)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )