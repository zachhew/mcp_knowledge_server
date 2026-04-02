from __future__ import annotations

from app.core.exceptions import ValidationAppError
from app.core.request_context import RequestContext


def require_scope(request_context: RequestContext, required_scope: str) -> None:
    if required_scope not in request_context.scopes:
        raise ValidationAppError(f"Missing required scope: {required_scope}")
