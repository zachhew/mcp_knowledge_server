from enum import StrEnum


class DocumentType(StrEnum):
    NOTE = "note"
    SPEC = "spec"
    RUNBOOK = "runbook"
    ADR = "adr"
    OTHER = "other"
