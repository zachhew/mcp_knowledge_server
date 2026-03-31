from __future__ import annotations

import uuid

from fastapi import Header, HTTPException, status

from app.core.request_context import RequestContext
from app.infrastructure.auth.api_key_auth import ApiKeyAuthService
from app.infrastructure.db.session import SessionFactory
from app.infrastructure.repositories.api_client_repository import SQLAlchemyApiClientRepository


async def build_request_context(
    x_api_key: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
) -> RequestContext:
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-api-key header",
        )

    async with SessionFactory() as session:
        repository = SQLAlchemyApiClientRepository(session)
        auth_service = ApiKeyAuthService(repository)
        authenticated_client = await auth_service.authenticate(x_api_key)

    request_id = x_request_id or str(uuid.uuid4())

    return RequestContext(
        request_id=request_id,
        client_id=authenticated_client.id,
        client_name=authenticated_client.name,
        scopes=authenticated_client.scopes,
    )