from project_wsx.core.logging import setup_logging

setup_logging()

from contextlib import asynccontextmanager

from fastapi import FastAPI

from project_wsx.api import api_router
from project_wsx.core.logging import logger
from project_wsx.core.settings import Settings
from project_wsx.core.database import init_db
from project_wsx.mcp.registry import register_all
from project_wsx.mcp.server import create_mcp

settings = Settings()

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
    lifespan=lifespan
)


@app.get("/")
def index():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


app.include_router(api_router, prefix="/api")
app.mount("/", mcp.streamable_http_app(), name="MCP Server")
