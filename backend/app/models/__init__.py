from app.models.user import User, Coach, Parent
from app.models.student import Student, CoachStudent
from app.models.training import TrainingRecord
from app.models.assessment import PhysicalAssessment
from app.models.comment import MonthlyComment
from app.models.promotion import PromotionSuggestion, ArchivedStudent

__all__ = [
    "User", "Coach", "Parent",
    "Student", "CoachStudent",
    "TrainingRecord",
    "PhysicalAssessment",
    "MonthlyComment",
    "PromotionSuggestion", "ArchivedStudent",
]
