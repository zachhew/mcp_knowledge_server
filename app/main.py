from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.transport.http.middleware import RequestContextMiddleware
from app.transport.http.routers.health import router as health_router
from app.transport.http.routers.mcp import router as mcp_router
from app.transport.http.routers.metrics import router as metrics_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application", extra={"app_env": settings.app_env})
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(metrics_router, prefix="/api/v1")
    app.include_router(mcp_router, prefix="/api/v1")

    return app


app = create_app()