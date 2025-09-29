from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from project_wsx import models, schemas
from project_wsx.db import get_db

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post("/", response_model=schemas.task_base.TaskRead)
def create_task(task: schemas.task_base.TaskCreate, db: Session = Depends(get_db)):
    existing_task = (
        db.query(models.Task).filter(models.Task.title == task.title).first()
    )
    if existing_task:
        raise HTTPException(status_code=422, detail="Task title must be unique.")

    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@tasks_router.get("/", response_model=list[schemas.task_base.TaskRead])
def list_tasks(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(5, ge=1, le=10, description="Max records to return"),
    search: str = Query(None, description="Search by title"),
):
    query = db.query(models.Task)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
    tasks = query.order_by(models.Task.id.desc()).offset(skip).limit(limit).all()
    return tasks


@tasks_router.get("/{task_id}", response_model=schemas.task_base.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@tasks_router.delete("/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully."}


@tasks_router.put("/{task_id}", response_model=schemas.task_base.TaskRead)
def update_task(
    task_id: int,
    task_update: schemas.task_base.TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    if task_update.title and task_update.title != task.title:
        existing_task = (
            db.query(models.Task).filter(models.Task.title == task_update.title).first()
        )
        if existing_task:
            raise HTTPException(status_code=422, detail="Task title must be unique.")

    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task
