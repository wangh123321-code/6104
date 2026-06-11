from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach
from app.models.student import Student
from app.models.assessment import PhysicalAssessment
from app.models.promotion import PromotionSuggestion
from app.schemas.promotion import PromotionSuggestionOut, PromotionConfirm
from app.schemas.response import success_response, error_response
from app.middleware.auth import (
    get_current_user,
    get_coach_for_user,
    check_student_access,
    require_role,
)

router = APIRouter(prefix="/api/promotions", tags=["晋升建议"])


@router.post("/generate/{year}/{quarter}")
def generate_promotion_suggestions(
    year: int,
    quarter: int,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    if quarter not in (1, 2, 3, 4):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("季度必须为1-4"),
        )
    coach = get_coach_for_user(current_user, db)

    db.query(PromotionSuggestion).filter(
        PromotionSuggestion.year == year,
        PromotionSuggestion.quarter == quarter,
    ).delete()

    from app.models.student import CoachStudent
    assigned_student_ids = [
        a.student_id for a in db.query(CoachStudent).filter(CoachStudent.coach_id == coach.id).all()
    ]
    if not assigned_student_ids:
        return success_response(data=[], message="无分配学员")

    quarter_week_map = {1: (1, 13), 2: (14, 26), 3: (27, 39), 4: (40, 53)}
    week_start, week_end = quarter_week_map[quarter]

    student_scores = []
    for sid in assigned_student_ids:
        assessments = (
            db.query(PhysicalAssessment)
            .filter(
                PhysicalAssessment.student_id == sid,
                PhysicalAssessment.year == year,
                PhysicalAssessment.week_number >= week_start,
                PhysicalAssessment.week_number <= week_end,
            )
            .all()
        )
        if assessments:
            avg_score = sum(a.total_score for a in assessments) / len(assessments)
            student_scores.append((sid, avg_score))

    if not student_scores:
        return success_response(data=[], message="该季度无评估数据")

    student_scores.sort(key=lambda x: x[1], reverse=True)

    top_30_count = max(1, int(len(student_scores) * 0.3))
    suggestions = []
    for idx, (sid, avg_score) in enumerate(student_scores):
        rank_pct = round((idx + 1) / len(student_scores) * 100, 2)
        auto_suggested = idx < top_30_count

        suggestion = PromotionSuggestion(
            student_id=sid,
            coach_id=coach.id,
            quarter=quarter,
            year=year,
            rank_percentage=rank_pct,
            auto_suggested=auto_suggested,
            status="suggested" if auto_suggested else "not_recommended",
            notes="自动生成：前30%推荐晋升" if auto_suggested else "自动生成：未进入前30%",
        )
        db.add(suggestion)
        suggestions.append(suggestion)

    db.commit()

    for s in suggestions:
        db.refresh(s)

    result = []
    for s in suggestions:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        item = PromotionSuggestionOut.model_validate(s).model_dump()
        item["student_name"] = student.name if student else "未知"
        result.append(item)

    return success_response(data=result, message="晋升建议已生成")


@router.get("/{year}/{quarter}")
def list_promotion_suggestions(
    year: int,
    quarter: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    suggestions = (
        db.query(PromotionSuggestion)
        .filter(PromotionSuggestion.year == year, PromotionSuggestion.quarter == quarter)
        .all()
    )
    result = []
    for s in suggestions:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        item = PromotionSuggestionOut.model_validate(s).model_dump()
        item["student_name"] = student.name if student else "未知"
        result.append(item)
    return success_response(data=result)


@router.put("/{suggestion_id}/confirm")
def confirm_promotion(
    suggestion_id: int,
    body: PromotionConfirm,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    coach = get_coach_for_user(current_user, db)
    suggestion = db.query(PromotionSuggestion).filter(PromotionSuggestion.id == suggestion_id).first()
    if suggestion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("晋升建议不存在"),
        )
    if suggestion.coach_id != coach.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("只能确认自己生成的建议"),
        )

    if body.status not in ("confirmed", "rejected", "suggested"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("状态值无效，仅支持 confirmed/rejected/suggested"),
        )

    suggestion.status = body.status
    suggestion.notes = body.notes or suggestion.notes
    db.commit()
    db.refresh(suggestion)

    student = db.query(Student).filter(Student.id == suggestion.student_id).first()
    item = PromotionSuggestionOut.model_validate(suggestion).model_dump()
    item["student_name"] = student.name if student else "未知"
    return success_response(data=item, message="晋升建议已更新")


@router.get("/student/{student_id}")
def get_student_promotion_history(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_student_access(current_user, student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权访问该学员数据"),
        )
    suggestions = (
        db.query(PromotionSuggestion)
        .filter(PromotionSuggestion.student_id == student_id)
        .order_by(PromotionSuggestion.year, PromotionSuggestion.quarter)
        .all()
    )
    student = db.query(Student).filter(Student.id == student_id).first()
    result = []
    for s in suggestions:
        item = PromotionSuggestionOut.model_validate(s).model_dump()
        item["student_name"] = student.name if student else "未知"
        result.append(item)
    return success_response(data=result)
