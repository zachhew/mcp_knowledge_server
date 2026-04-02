from __future__ import annotations

import hashlib

import pytest

from app.core.exceptions import NotFoundError, ValidationAppError
from app.infrastructure.auth.api_key_auth import ApiKeyAuthService


class FakeClient:
    def __init__(self, *, client_id: str, name: str, scopes: str, is_active: bool) -> None:
        self.id = client_id
        self.name = name
        self.scopes = scopes
        self.is_active = is_active


class FakeRepo:
    def __init__(self, client: FakeClient | None) -> None:
        self._client = client

    async def get_by_hashed_api_key(self, hashed_api_key: str):
        if self._client is None:
            return None
        expected = hashlib.sha256(b"valid-key").hexdigest()
        if hashed_api_key == expected:
            return self._client
        return None


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    client = FakeClient(
        client_id="client-1",
        name="test-client",
        scopes="knowledge:read,tasks:write",
        is_active=True,
    )
    service = ApiKeyAuthService(FakeRepo(client))

    result = await service.authenticate("valid-key")

    assert result.name == "test-client"
    assert "knowledge:read" in result.scopes
    assert "tasks:write" in result.scopes


@pytest.mark.asyncio
async def test_authenticate_rejects_empty_key() -> None:
    service = ApiKeyAuthService(FakeRepo(None))

    with pytest.raises(ValidationAppError):
        await service.authenticate("")


@pytest.mark.asyncio
async def test_authenticate_rejects_invalid_key() -> None:
    service = ApiKeyAuthService(FakeRepo(None))

    with pytest.raises(NotFoundError):
        await service.authenticate("wrong-key")
