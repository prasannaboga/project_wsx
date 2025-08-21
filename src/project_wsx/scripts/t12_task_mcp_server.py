from datetime import datetime
import asyncio
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP(
    "task_mcp_server", host="127.0.0.1", port=8001, log_level="DEBUG", debug=True
)

# Fake in-memory database
tasks = {}


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

    for i in range(1, 4):
        await asyncio.sleep(5)
        await ctx.report_progress(progress=i * 33, total=100)

    task_id = f"task_{len(tasks)+1}"
    tasks[task_id] = {
        "title": title,
        "due_date": due_date,
        "created": datetime.now().isoformat(),
    }

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
    mcp.run(transport="stdio")


# -------------------------
# 🚀 Run
# -------------------------
if __name__ == "__main__":
    main()
