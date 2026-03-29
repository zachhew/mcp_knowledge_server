from __future__ import annotations

import logging

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.transport.mcp.registry import ToolRegistry
from app.transport.mcp.result import ToolExecutionResult

logger = logging.getLogger(__name__)


class MCPDispatcher:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def list_tools(self) -> list[dict]:
        return self._registry.list_definitions()

    async def call_tool(
        self,
        session: AsyncSession,
        tool_name: str,
        arguments: dict,
    ) -> ToolExecutionResult:
        logger.info("Calling MCP tool: %s", tool_name)

        try:
            tool = self._registry.get(tool_name)
            parsed_input = tool.input_model(**arguments)
            raw_result = await tool.handler(session, parsed_input)
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