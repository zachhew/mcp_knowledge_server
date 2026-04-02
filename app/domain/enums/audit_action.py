from enum import StrEnum


class AuditAction(StrEnum):
    TOOL_CALL = "tool_call"
    TASK_CREATED = "task_created"
    NOTE_CREATED = "note_created"
    DOCUMENT_READ = "document_read"
    SEARCH_EXECUTED = "search_executed"
