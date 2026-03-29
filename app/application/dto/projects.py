from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class ProjectDTO:
    id: UUID
    slug: str
    name: str
    description: str | None
    owner: str
    tags: str | None