from __future__ import annotations

from fastapi import FastAPI
from fastapi.routing import APIRouter

from config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    router = APIRouter()

    @router.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

    @router.get("/")
    async def root() -> dict[str, str]:
        return {"message": f"Welcome to {settings.app_name}"}

    app.include_router(router)
    return app


app = create_app()
