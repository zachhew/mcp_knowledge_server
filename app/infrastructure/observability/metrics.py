from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

MCP_TOOL_CALLS_TOTAL = Counter(
    "mcp_tool_calls_total",
    "Total MCP tool calls",
    ["tool_name", "outcome"],
)

MCP_TOOL_DURATION_SECONDS = Histogram(
    "mcp_tool_duration_seconds",
    "MCP tool execution duration in seconds",
    ["tool_name"],
)
