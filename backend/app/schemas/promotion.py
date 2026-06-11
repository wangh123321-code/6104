from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PromotionSuggestionOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    coach_id: Optional[int] = None
    quarter: int
    year: int
    rank_percentage: float
    auto_suggested: bool
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromotionConfirm(BaseModel):
    status: str
    notes: Optional[str] = ""
