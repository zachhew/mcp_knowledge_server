from __future__ import annotations

import logging

from pydantic import ValidationError

from app.core.exceptions import AppError
from app.core.telemetry import Timer
from app.transport.mcp.auth import require_scope
from app.transport.mcp.context import ToolExecutionContext
from app.transport.mcp.registry import ToolRegistry
from app.transport.mcp.result import ToolExecutionResult
from app.infrastructure.observability.metrics import (
    MCP_TOOL_CALLS_TOTAL,
    MCP_TOOL_DURATION_SECONDS,
)

logger = logging.getLogger(__name__)


class MCPDispatcher:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def list_tools(self) -> list[dict]:
        return self._registry.list_definitions()

    async def call_tool(
        self,
        execution_context: ToolExecutionContext,
        tool_name: str,
        arguments: dict,
    ) -> ToolExecutionResult:
        session = execution_context.db_session
        request_context = execution_context.request_context

        logger.info(
            "Calling MCP tool",
            extra={
                "request_id": request_context.request_id,
                "client_name": request_context.client_name,
                "tool_name": tool_name,
            },
        )

        try:
            tool = self._registry.get(tool_name)
            require_scope(request_context, tool.required_scope)

            with Timer() as timer:
                parsed_input = tool.input_model(**arguments)
                raw_result = await tool.handler(execution_context, parsed_input)
                parsed_output = tool.output_model(**raw_result)

            MCP_TOOL_CALLS_TOTAL.labels(tool_name=tool_name, outcome="success").inc()
            MCP_TOOL_DURATION_SECONDS.labels(tool_name=tool_name).observe(timer.elapsed)

            logger.info(
                "MCP tool completed",
                extra={
                    "request_id": request_context.request_id,
                    "client_name": request_context.client_name,
                    "tool_name": tool_name,
                    "duration_ms": round(timer.elapsed * 1000, 2),
                    "outcome": "success",
                },
            )

            return ToolExecutionResult(
                tool_name=tool_name,
                content=parsed_output.model_dump(mode="json"),
                is_error=False,
                error_message=None,
            )

        except ValidationError as exc:
            MCP_TOOL_CALLS_TOTAL.labels(tool_name=tool_name, outcome="validation_error").inc()
            logger.warning("Tool validation failed for %s: %s", tool_name, exc)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )

        except AppError as exc:
            MCP_TOOL_CALLS_TOTAL.labels(tool_name=tool_name, outcome="app_error").inc()
            logger.warning("Application error for %s: %s", tool_name, exc)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )

        except ValueError as exc:
            MCP_TOOL_CALLS_TOTAL.labels(tool_name=tool_name, outcome="value_error").inc()
            logger.warning("Tool execution rejected for %s: %s", tool_name, exc)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )

        except Exception as exc:
            MCP_TOOL_CALLS_TOTAL.labels(tool_name=tool_name, outcome="unhandled_error").inc()
            logger.exception("Unhandled tool execution error for %s", tool_name)
            await session.rollback()
            return ToolExecutionResult(
                tool_name=tool_name,
                content={},
                is_error=True,
                error_message=str(exc),
            )
