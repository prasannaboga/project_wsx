import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from project_wsx.db import init_db
from project_wsx.api import api_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Initializing database...")
    init_db()
    yield
    logger.debug("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index():
    return {"Hello": "World"}


app.include_router(api_router, prefix="/api")
