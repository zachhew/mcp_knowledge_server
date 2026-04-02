from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class AuthenticatedClientDTO:
    id: UUID
    name: str
    scopes: frozenset[str]
    is_active: bool
