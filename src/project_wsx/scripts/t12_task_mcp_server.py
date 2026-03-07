import asyncio
import json
import os
from asyncio import tasks
from datetime import datetime

import requests
from jose import jwt
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import Context, FastMCP
from pydantic import AnyHttpUrl

from project_wsx.core.logging import logger
from project_wsx.core.settings import Settings

logger.info("Starting Task MCP Server...")
settings = Settings()


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_scopes(value: str | None) -> list[str]:
    if not value:
        return []
    return [scope for scope in value.split() if scope]


class Auth0TokenVerifier(TokenVerifier):
    def __init__(self, issuer: str, audience: str) -> None:
        self.issuer = issuer    
        self.audience = audience
        jwks_url = f"{issuer}/.well-known/jwks.json"
        self.jwks = requests.get(jwks_url).json()["keys"]
        
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = jwt.decode(
                token,
                self.jwks,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
        
        return AccessToken(
            sub=payload.get("sub"),
            scopes=payload.get("scope", "").split(),
            expires_at=payload.get("exp"),
            issued_at=payload.get("iat"),
            raw=payload
        )


auth_settings = None
token_verifier = None
if settings.mcp_auth_enabled:
    logger.info("MCP Authentication is ENABLED. Configuring auth settings...")
    auth_settings = AuthSettings(
        issuer_url=AnyHttpUrl("https://prasannaboga-dev.us.auth0.com"),
        resource_server_url=AnyHttpUrl("https://prasannaboga-dev.us.auth0.com/api/v2/"),
    )
    token_verifier = Auth0TokenVerifier("https://prasannaboga-dev.us.auth0.com", "https://prasannaboga-dev.us.auth0.com/api/v2/")

mcp = FastMCP(
    "task_mcp_server",
    host="127.0.0.1",
    port=8002,
    stateless_http=True,
    json_response=True,
    log_level="DEBUG",
    debug=True,
    auth=auth_settings,
    token_verifier=token_verifier,
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
