from fastapi import APIRouter
from .routers import tasks

api_router = APIRouter()
api_router.include_router(tasks.tasks_router)