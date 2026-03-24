#!/usr/bin/env python

from datetime import date

from project_wsx.core.database import get_db_context
from project_wsx.models.task import Task


def delete_old_tasks():
    cutoff = date(2025, 12, 31)

    with get_db_context() as db:
        deleted = (
            db.query(Task)
            .filter(Task.created_at < cutoff)
            .delete(synchronize_session=False)
        )
        db.commit()

    print(f"Deleted {deleted} tasks older than {cutoff}")


if __name__ == "__main__":
    delete_old_tasks()
