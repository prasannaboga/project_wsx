import json

from project_wsx.core.logging import logger, setup_logging

setup_logging()  # noqa: E402 — must run before other imports trigger logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from project_wsx.api import api_router
from project_wsx.core.database import init_db
from project_wsx.core.settings import Settings
from project_wsx.mcp.middleware import AuthHeaderMiddleware, MCPPathMiddleware
from project_wsx.mcp.oauth import oauth_router
from project_wsx.mcp.registry import register_all
from project_wsx.mcp.server import create_mcp

settings = Settings()
logger.debug(f"Loaded settings: {settings.model_dump()}")

mcp = create_mcp()
register_all(mcp)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Initializing database...")
    init_db()
    async with mcp.session_manager.run():
        logger.debug("MCP server is running...")
        yield

    logger.debug("Shutting down...")


app = FastAPI(
    title="Project WSX API",
    description="API for Project WSX",
    version="0.1.2",
    lifespan=lifespan,
)


app.add_middleware(AuthHeaderMiddleware)
app.add_middleware(MCPPathMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


app.include_router(oauth_router)
app.include_router(api_router, prefix="/api")
app.mount("/mcp", mcp.streamable_http_app(), name="MCP Server")
app.router.redirect_slashes = False
