from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach
from app.models.student import Student
from app.models.assessment import PhysicalAssessment
from app.models.promotion import ArchivedStudent
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentOut,
    GrowthCurvePoint,
    GrowthCurveResponse,
)
from app.schemas.response import success_response, error_response
from app.middleware.auth import (
    get_current_user,
    get_coach_for_user,
    check_student_access,
    require_role,
)

router = APIRouter(prefix="/api/assessments", tags=["体测评估"])


@router.post("")
def create_or_update_assessment(
    body: AssessmentCreate,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    if not check_student_access(current_user, body.student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权为该学员录入评估"),
        )

    total = round(
        (body.speed_score + body.strength_score + body.endurance_score
         + body.agility_score + body.flexibility_score) / 5,
        2,
    )

    existing = db.query(PhysicalAssessment).filter(
        PhysicalAssessment.student_id == body.student_id,
        PhysicalAssessment.week_number == body.week_number,
        PhysicalAssessment.year == body.year,
    ).first()

    if existing:
        existing.speed_score = body.speed_score
        existing.strength_score = body.strength_score
        existing.endurance_score = body.endurance_score
        existing.agility_score = body.agility_score
        existing.flexibility_score = body.flexibility_score
        existing.total_score = total
        db.commit()
        db.refresh(existing)
        return success_response(
            data=AssessmentOut.model_validate(existing).model_dump(),
            message="评估记录已更新",
        )

    record = PhysicalAssessment(
        student_id=body.student_id,
        week_number=body.week_number,
        year=body.year,
        speed_score=body.speed_score,
        strength_score=body.strength_score,
        endurance_score=body.endurance_score,
        agility_score=body.agility_score,
        flexibility_score=body.flexibility_score,
        total_score=total,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return success_response(
        data=AssessmentOut.model_validate(record).model_dump(),
        message="评估记录创建成功",
    )


@router.get("/student/{student_id}")
def list_assessments_for_student(
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
    query = db.query(PhysicalAssessment).filter(PhysicalAssessment.student_id == student_id)
    if year:
        query = query.filter(PhysicalAssessment.year == year)
    records = query.order_by(PhysicalAssessment.year, PhysicalAssessment.week_number).all()
    return success_response(data=[AssessmentOut.model_validate(r).model_dump() for r in records])


@router.get("/growth-curve/{student_id}")
def get_growth_curve(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_student_access(current_user, student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权访问该学员数据"),
        )
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("学员不存在"),
        )

    records = (
        db.query(PhysicalAssessment)
        .filter(PhysicalAssessment.student_id == student_id)
        .order_by(PhysicalAssessment.year, PhysicalAssessment.week_number)
        .all()
    )

    points = [
        GrowthCurvePoint(
            week_number=r.week_number,
            year=r.year,
            total_score=r.total_score,
            speed_score=r.speed_score,
            strength_score=r.strength_score,
            endurance_score=r.endurance_score,
            agility_score=r.agility_score,
            flexibility_score=r.flexibility_score,
        )
        for r in records
    ]

    response = GrowthCurveResponse(
        student_id=student_id,
        student_name=student.name,
        points=points,
    )
    return success_response(data=response.model_dump())


@router.post("/archive/{year}")
def archive_year_data(
    year: int,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    students = db.query(Student).filter(Student.enrollment_year == year, Student.status == "active").all()
    archived_count = 0
    for student in students:
        existing_archive = db.query(ArchivedStudent).filter(
            ArchivedStudent.original_student_id == student.id,
            ArchivedStudent.archive_year == year,
        ).first()
        if existing_archive:
            continue

        assessments = db.query(PhysicalAssessment).filter(
            PhysicalAssessment.student_id == student.id,
            PhysicalAssessment.year == year,
        ).all()

        snapshot = {
            "name": student.name,
            "gender": student.gender,
            "birth_date": student.birth_date.isoformat() if student.birth_date else None,
            "group_name": student.group_name,
            "enrollment_year": student.enrollment_year,
            "assessments": [
                {
                    "week_number": a.week_number,
                    "total_score": a.total_score,
                    "speed_score": a.speed_score,
                    "strength_score": a.strength_score,
                    "endurance_score": a.endurance_score,
                    "agility_score": a.agility_score,
                    "flexibility_score": a.flexibility_score,
                }
                for a in assessments
            ],
        }

        archive = ArchivedStudent(
            original_student_id=student.id,
            archive_year=year,
            snapshot_data=snapshot,
        )
        db.add(archive)
        student.status = "archived"
        archived_count += 1

    db.commit()
    return success_response(data={"archived_count": archived_count, "year": year}, message="归档完成")
