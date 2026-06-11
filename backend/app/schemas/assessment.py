from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    student_id: int
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2000, le=2100)
    speed_score: float = Field(..., ge=0, le=100)
    strength_score: float = Field(..., ge=0, le=100)
    endurance_score: float = Field(..., ge=0, le=100)
    agility_score: float = Field(..., ge=0, le=100)
    flexibility_score: float = Field(..., ge=0, le=100)


class AssessmentOut(BaseModel):
    id: int
    student_id: int
    week_number: int
    year: int
    speed_score: float
    strength_score: float
    endurance_score: float
    agility_score: float
    flexibility_score: float
    total_score: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GrowthCurvePoint(BaseModel):
    week_number: int
    year: int
    total_score: float
    speed_score: float
    strength_score: float
    endurance_score: float
    agility_score: float
    flexibility_score: float


class GrowthCurveResponse(BaseModel):
    student_id: int
    student_name: str
    points: list[GrowthCurvePoint]
