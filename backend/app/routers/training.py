from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach
from app.models.training import TrainingRecord
from app.schemas.training import TrainingRecordCreate, TrainingRecordOut
from app.schemas.response import success_response, error_response
from app.middleware.auth import (
    get_current_user,
    get_coach_for_user,
    check_student_access,
    require_role,
)

router = APIRouter(prefix="/api/training", tags=["训练记录"])


@router.post("")
def create_or_update_training(
    body: TrainingRecordCreate,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    coach = get_coach_for_user(current_user, db)
    if not check_student_access(current_user, body.student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权为该学员录入训练记录"),
        )

    existing = db.query(TrainingRecord).filter(
        TrainingRecord.student_id == body.student_id,
        TrainingRecord.week_number == body.week_number,
        TrainingRecord.year == body.year,
    ).first()

    if existing:
        existing.technique_score = body.technique_score
        existing.fitness_score = body.fitness_score
        existing.match_score = body.match_score
        existing.notes = body.notes
        existing.coach_id = coach.id
        db.commit()
        db.refresh(existing)
        return success_response(
            data=TrainingRecordOut.model_validate(existing).model_dump(),
            message="训练记录已更新",
        )

    record = TrainingRecord(
        student_id=body.student_id,
        coach_id=coach.id,
        week_number=body.week_number,
        year=body.year,
        technique_score=body.technique_score,
        fitness_score=body.fitness_score,
        match_score=body.match_score,
        notes=body.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return success_response(
        data=TrainingRecordOut.model_validate(record).model_dump(),
        message="训练记录创建成功",
    )


@router.get("/student/{student_id}")
def list_training_for_student(
    student_id: int,
    year: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_student_access(current_user, student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权访问该学员数据"),
        )
    query = db.query(TrainingRecord).filter(TrainingRecord.student_id == student_id)
    if year:
        query = query.filter(TrainingRecord.year == year)
    records = query.order_by(TrainingRecord.year, TrainingRecord.week_number).all()
    return success_response(data=[TrainingRecordOut.model_validate(r).model_dump() for r in records])


@router.get("/{record_id}")
def get_training_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(TrainingRecord).filter(TrainingRecord.id == record_id).first()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("训练记录不存在"),
        )
    if not check_student_access(current_user, record.student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权访问该记录"),
        )
    return success_response(data=TrainingRecordOut.model_validate(record).model_dump())
