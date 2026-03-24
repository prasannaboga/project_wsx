from datetime import datetime

from mcp.server.fastmcp import Context

from project_wsx.core.database import get_db, get_db_context
from project_wsx.core.logging import logger
from project_wsx.models.task import Task
from project_wsx.schemas.task_base import TaskRead


def register(mcp):
    @mcp.tool()
    async def create_task(title: str, due_date: str) -> dict:
        parsed_due_date = datetime.fromisoformat(due_date)

        with get_db_context() as db:
            existing_task = db.query(Task).filter(Task.title == title).first()
            if existing_task:
                raise ValueError(f"A task with the title '{title}' already exists.")

            task = Task(title=title, due_date=parsed_due_date)
            db.add(task)
            db.commit()
            db.refresh(task)

            return TaskRead.model_validate(task).model_dump(mode="json")

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

    @mcp.tool()
    def list_tasks(
        search: str = "",
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict]:
        """
        List tasks with optional title search and pagination.

        Args:
            search: Partial title to filter by (case-insensitive).
            skip:   Number of records to skip (for pagination).
            limit:  Maximum number of records to return (max 50).

        Returns:
            A list of task dicts ordered by newest first.
        """
        limit = min(limit, 10)

        with get_db_context() as db:
            query = db.query(Task)
            if search:
                query = query.filter(Task.title.ilike(f"%{search}%"))
            tasks = query.order_by(Task.id.desc()).offset(skip).limit(limit).all()
            return [
                TaskRead.model_validate(task).model_dump(mode="json") for task in tasks
            ]

    @mcp.tool()
    def update_task(
        task_id: int,
        title: str = "",
        due_date: str = "",
        status: str = "",
    ) -> dict:
        """
        Update one or more fields on an existing task.
        Only the fields you provide will be changed.

        Args:
            task_id:  ID of the task to update.
            title:    New title (leave blank to keep current).
            due_date: New due date in ISO format (leave blank to keep current).
            status:   New status — 'pending', 'in_progress', or 'done'
                      (leave blank to keep current).

        Returns:
            The updated task as a dict, or an error message.
        """
        VALID_STATUSES = {"pending", "in_progress", "done", "skipped"}

        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"error": f"Task {task_id} not found."}

            if title and title != task.title:
                conflict = db.query(Task).filter(Task.title == title).first()
                if conflict:
                    return {"error": f"A task with title '{title}' already exists."}
                task.title = title

            if due_date:
                task.due_date = datetime.fromisoformat(due_date)

            if status:
                if status not in VALID_STATUSES:
                    return {
                        "error": f"Invalid status '{status}'. Choose from {VALID_STATUSES}."
                    }
                task.status = status

            db.flush()
            return TaskRead.model_validate(task).model_dump(mode="json")

    @mcp.tool()
    def delete_task(task_id: int) -> dict:
        """
        Permanently delete a task by ID.

        Args:
            task_id: ID of the task to delete.

        Returns:
            A success or error message.
        """
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"error": f"Task {task_id} not found."}
            db.delete(task)
            return {
                "detail": f"Task '{task.title}' (id={task_id}) deleted successfully."
            }
