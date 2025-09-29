from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    due_date: datetime


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
