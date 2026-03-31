from __future__ import annotations

from fastapi import Header, HTTPException, Request, status

from app.core.request_context import RequestContext
from app.infrastructure.auth.api_key_auth import ApiKeyAuthService
from app.infrastructure.db.session import SessionFactory
from app.infrastructure.repositories.api_client_repository import SQLAlchemyApiClientRepository


async def build_request_context(
    request: Request,
    x_api_key: str | None = Header(default=None),
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

    request_id = getattr(request.state, "request_id", None)
    if request_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request context is not initialized",
        )

    return RequestContext(
        request_id=request_id,
        client_id=authenticated_client.id,
        client_name=authenticated_client.name,
        scopes=authenticated_client.scopes,
    )