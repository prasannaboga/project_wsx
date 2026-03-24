import logging
import sys

from loguru import logger

logger.remove()


def format_row(row):
    base = (
        "<green>{time:YYYY-MM-DDTHH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    # Only print extra if present and not empty
    if row["extra"]:
        base += " | <cyan>{extra}</cyan>"
    return base + "\n"


logger.add(
    sys.stdout,
    format=format_row,
    level="DEBUG",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# ── Intercept stdlib logging → loguru ────────────────────────────────────────
# uvicorn, FastAPI, and FastMCP all use stdlib logging.
# This handler catches every stdlib log record and re-emits it through loguru,
# so everything appears with your format and colours.
class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Match stdlib level name to loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
 
        # Walk the call stack to find the real caller (skip logging internals)
        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
 
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
 
 
def setup_logging(level: str = "DEBUG") -> None:
    """
    Call once at startup (before uvicorn/FastMCP init).
    Routes all stdlib logging through loguru.
    """
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
 
    # Ensure uvicorn loggers propagate to the root (don't install their own handlers)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "mcp"):
        log = logging.getLogger(name)
        log.handlers = [_InterceptHandler()]
        log.propagate = False
