from __future__ import annotations

import hashlib

from app.application.dto.auth import AuthenticatedClientDTO
from app.application.interfaces.repositories import ApiClientRepositoryProtocol
from app.core.exceptions import NotFoundError, ValidationAppError


class ApiKeyAuthService:
    def __init__(self, repository: ApiClientRepositoryProtocol) -> None:
        self._repository = repository

    @staticmethod
    def hash_api_key(raw_api_key: str) -> str:
        return hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()

    async def authenticate(self, raw_api_key: str) -> AuthenticatedClientDTO:
        if not raw_api_key.strip():
            raise ValidationAppError("API key must not be empty")

        hashed_api_key = self.hash_api_key(raw_api_key)
        client = await self._repository.get_by_hashed_api_key(hashed_api_key)

        if client is None or not client.is_active:
            raise NotFoundError("Invalid API key")

        scopes = frozenset(item.strip() for item in client.scopes.split(",") if item.strip())

        return AuthenticatedClientDTO(
            id=client.id,
            name=client.name,
            scopes=scopes,
            is_active=client.is_active,
        )
