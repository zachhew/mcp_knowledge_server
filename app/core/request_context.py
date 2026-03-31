from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet
from uuid import UUID


@dataclass(slots=True, frozen=True)
class RequestContext:
    request_id: str
    client_id: UUID
    client_name: str
    scopes: FrozenSet[str]