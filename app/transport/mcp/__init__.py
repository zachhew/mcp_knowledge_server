from app.transport.mcp.dispatcher import MCPDispatcher
from app.transport.mcp.registry import ToolRegistry
from app.transport.mcp.tools.build_project_context import (
    BuildProjectContextInput,
    BuildProjectContextOutput,
    build_project_context_handler,
)
from app.transport.mcp.tools.create_note import (
    CreateNoteInput,
    CreateNoteOutput,
    create_note_handler,
)
from app.transport.mcp.tools.create_task import (
    CreateTaskInput,
    CreateTaskOutput,
    create_task_handler,
)
from app.transport.mcp.tools.get_document import (
    GetDocumentInput,
    GetDocumentOutput,
    get_document_handler,
)
from app.transport.mcp.tools.search_knowledge import (
    SearchKnowledgeInput,
    SearchKnowledgeOutput,
    search_knowledge_handler,
)
from app.transport.mcp.tools.search_tasks import (
    SearchTasksInput,
    SearchTasksOutput,
    search_tasks_handler,
)

registry = ToolRegistry()

registry.register(
    name="search_knowledge",
    description="Searches knowledge documents by text query and optional project filter.",
    input_model=SearchKnowledgeInput,
    output_model=SearchKnowledgeOutput,
    required_scope="knowledge:read",
    handler=search_knowledge_handler,
)

registry.register(
    name="get_document",
    description="Returns a full document by its identifier.",
    input_model=GetDocumentInput,
    output_model=GetDocumentOutput,
    required_scope="knowledge:read",
    handler=get_document_handler,
)

registry.register(
    name="build_project_context",
    description="Builds structured project context including recent documents and open tasks.",
    input_model=BuildProjectContextInput,
    output_model=BuildProjectContextOutput,
    required_scope="projects:read",
    handler=build_project_context_handler,
)

registry.register(
    name="search_tasks",
    description="Searches tasks by text query, project, or assignee.",
    input_model=SearchTasksInput,
    output_model=SearchTasksOutput,
    required_scope="tasks:read",
    handler=search_tasks_handler,
)

registry.register(
    name="create_task",
    description="Creates a task inside a project.",
    input_model=CreateTaskInput,
    output_model=CreateTaskOutput,
    required_scope="tasks:write",
    handler=create_task_handler,
)

registry.register(
    name="create_note",
    description="Creates a note inside a project.",
    input_model=CreateNoteInput,
    output_model=CreateNoteOutput,
    required_scope="notes:write",
    handler=create_note_handler,
)

dispatcher = MCPDispatcher(registry)

__all__ = ["dispatcher", "registry"]
