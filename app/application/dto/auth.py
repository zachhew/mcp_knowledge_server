from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet
from uuid import UUID


@dataclass(slots=True, frozen=True)
class AuthenticatedClientDTO:
    id: UUID
    name: str
    scopes: FrozenSet[str]
    is_active: bool
