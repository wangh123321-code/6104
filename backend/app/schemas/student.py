from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., pattern=r"^(男|女)$")
    birth_date: date
    group_name: str = Field(default="", max_length=50)
    enrollment_year: int = Field(..., ge=2000, le=2100)
    parent_user_id: Optional[int] = None
    relationship: Optional[str] = "家长"


class StudentOut(BaseModel):
    id: int
    name: str
    gender: str
    birth_date: date
    group_name: str
    enrollment_year: int
    parent_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentDetailOut(StudentOut):
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_relationship: Optional[str] = None
    coaches: list[dict] = []
