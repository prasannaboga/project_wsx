import asyncio
import json
import os
from asyncio import tasks
from datetime import datetime

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP(
    "task_mcp_server", host="127.0.0.1", port=8002, log_level="DEBUG", debug=True
)

DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")


def save_tasks(tasks):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return {}


tasks = load_tasks()


# -------------------------
# 🔹 TOOL: Add a new task
# -------------------------
@mcp.tool(
    name="add_task",
    title="Add Task",
    description="Add a new task with a due date (YYYY-MM-DD)",
)
async def add_task(title: str, due_date: str, ctx: Context) -> str:
    """
    Add a new task with a due date (YYYY-MM-DD).
    Returns the task ID.
    """
    await ctx.info(f"Adding new task '{title}'...")

    task_id = f"task_{len(tasks)+1}"
    tasks[task_id] = {
        "title": title,
        "due_date": due_date,
        "created": datetime.now().isoformat(),
    }

    save_tasks(tasks)  # Save tasks to file

    await ctx.info(f"Task '{title}' added successfully ✅")
    return f"Task '{title}' added with ID {task_id}"


# -------------------------
# 🔹 RESOURCE: Query tasks
# -------------------------
@mcp.resource("tasks://all")
def get_all_tasks():
    """
    Return all tasks as a resource.
    """
    return {"tasks": tasks}


@mcp.resource("tasks://{task_id}")
def get_task(task_id: str):
    """
    Return details of a single task.
    """
    if task_id not in tasks:
        raise ValueError(f"No task found with ID {task_id}")
    return tasks[task_id]


# -------------------------
# 🔹 PROMPT: Create summary
# -------------------------
@mcp.prompt("task_summary")
def task_summary_prompt(user_name: str):
    """
    Generate a summary email of all tasks for a given user.
    """
    # Pull tasks from the "resource"
    task_list = (
        "\n".join(f"- {t['title']} (due {t['due_date']})" for t in tasks.values())
        or "No tasks available."
    )

    return f"""
Write a short professional email to {user_name}, summarizing their tasks:

{task_list}
    """


def main():
    mcp.run(transport="streamable-http")


# -------------------------
# 🚀 Run
# -------------------------
if __name__ == "__main__":
    main()
