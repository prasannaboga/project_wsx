from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from project_wsx import models, schemas
from project_wsx.db import get_db

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post("/", response_model=schemas.task_base.TaskRead)
def create_task(task: schemas.task_base.TaskCreate, db: Session = Depends(get_db)):
    existing_task = db.query(models.Task).filter(models.Task.title == task.title).first()
    if existing_task:
        raise HTTPException(status_code=422, detail="Task title must be unique.")

    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
