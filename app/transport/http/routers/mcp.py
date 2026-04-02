from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import RequestContext
from app.infrastructure.db.session import get_db_session
from app.transport.http.dependencies import build_request_context
from app.transport.mcp import dispatcher
from app.transport.mcp.context import ToolExecutionContext
from app.transport.mcp.schemas import JsonRpcError, JsonRpcRequest, JsonRpcResponse, ToolCallParams

router = APIRouter(tags=["mcp"])

METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


@router.post("/mcp", response_model=JsonRpcResponse)
async def mcp_endpoint(
    request: JsonRpcRequest,
    session: AsyncSession = Depends(get_db_session),
    request_context: RequestContext = Depends(build_request_context),
) -> JsonRpcResponse:
    params = request.params or {}

    try:
        if request.method == "tools/list":
            tools = await dispatcher.list_tools()
            return JsonRpcResponse(
                id=request.id,
                result={"tools": tools},
            )

        if request.method == "tools/call":
            tool_request = ToolCallParams(**params)
            execution_context = ToolExecutionContext(
                db_session=session,
                request_context=request_context,
            )

            result = await dispatcher.call_tool(
                execution_context=execution_context,
                tool_name=tool_request.name,
                arguments=tool_request.arguments,
            )

            if result.is_error:
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcError(
                        code=INVALID_PARAMS,
                        message=result.error_message or "Tool call failed",
                    ),
                )

            return JsonRpcResponse(
                id=request.id,
                result={
                    "toolName": result.tool_name,
                    "content": result.content,
                },
            )

        return JsonRpcResponse(
            id=request.id,
            error=JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Unknown method: {request.method}",
            ),
        )

    except Exception as exc:
        return JsonRpcResponse(
            id=request.id,
            error=JsonRpcError(
                code=INTERNAL_ERROR,
                message=str(exc),
            ),
        )
