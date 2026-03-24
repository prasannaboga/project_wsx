from datetime import datetime

from mcp.server.fastmcp import Context

from project_wsx.core.database import get_db_context
from project_wsx.core.logging import logger
from project_wsx.models.task import Task
from project_wsx.schemas.task_base import TaskRead


def register(mcp):
    @mcp.tool()
    async def get_task_id(task_id: int, ctx: Context) -> dict:
        with get_db_context() as db:
            logger.debug(f"Received request to fetch task with ID {task_id}")
            await ctx.info(f"Fetching task with ID {task_id}")
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                await ctx.error(f"No task found with ID {task_id}")
                raise ValueError(f"No task found with ID {task_id}")
            return TaskRead.model_validate(task).model_dump(mode="json")
