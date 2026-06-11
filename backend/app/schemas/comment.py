from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    student_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    content: str = Field(..., min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)
    force: bool = False


class CommentOut(BaseModel):
    id: int
    student_id: int
    coach_id: int
    coach_name: Optional[str] = None
    month: int
    year: int
    content: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentConflictOut(BaseModel):
    current_version: int
    current_content: str
    your_version: int
    your_content: str
