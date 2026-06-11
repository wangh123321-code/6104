from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TrainingRecordCreate(BaseModel):
    student_id: int
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2000, le=2100)
    technique_score: float = Field(..., ge=0, le=100)
    fitness_score: float = Field(..., ge=0, le=100)
    match_score: float = Field(..., ge=0, le=100)
    notes: str = Field(default="")


class TrainingRecordOut(BaseModel):
    id: int
    student_id: int
    coach_id: int
    week_number: int
    year: int
    technique_score: float
    fitness_score: float
    match_score: float
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
