from loguru import logger
import sys


logger.remove()


def format_row(row):
    base = (
        "<green>{time:YYYY-MM-DDTHH:mm:ss}</green> | "
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
