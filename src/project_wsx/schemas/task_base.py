from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class TaskBase(BaseModel):
    title: str
    due_date: datetime
    status: str | None = "pending"


class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v):
        if not v or not v.strip():
            raise ValueError("Title must not be blank")
        return v

    @field_validator("due_date")
    @classmethod
    def due_date_must_not_be_blank(cls, v):
        if not v:
            raise ValueError("Due date must not be blank")
        return v


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def title_must_not_be_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title must not be blank")
        return v

    @field_validator("due_date", mode="before")
    @classmethod
    def due_date_must_not_be_blank(cls, v):
        if v is not None and not v:
            raise ValueError("Due date must not be blank")
        return v


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
