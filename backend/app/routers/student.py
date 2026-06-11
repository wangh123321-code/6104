from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach, Parent
from app.models.student import Student, CoachStudent
from app.schemas.student import StudentCreate, StudentOut, StudentDetailOut
from app.schemas.response import success_response, error_response
from app.middleware.auth import (
    get_current_user,
    get_coach_for_user,
    get_parent_for_user,
    get_accessible_student_ids,
    check_student_access,
    require_role,
)

router = APIRouter(prefix="/api/students", tags=["学员"])


@router.get("")
def list_students(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accessible_ids = get_accessible_student_ids(current_user, db)
    if not accessible_ids:
        return success_response(data=[])
    students = db.query(Student).filter(Student.id.in_(accessible_ids), Student.status == "active").all()
    return success_response(data=[StudentOut.model_validate(s).model_dump() for s in students])


@router.get("/{student_id}")
def get_student(student_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

    parent_name = None
    parent_phone = None
    parent_relationship = None
    if student.parent_id:
        parent = db.query(Parent).filter(Parent.id == student.parent_id).first()
        if parent:
            parent_user = db.query(User).filter(User.id == parent.user_id).first()
            if parent_user:
                parent_name = parent_user.name
                parent_phone = parent_user.phone
                parent_relationship = parent.kinship

    coaches = []
    associations = db.query(CoachStudent).filter(CoachStudent.student_id == student_id).all()
    for assoc in associations:
        coach = db.query(Coach).filter(Coach.id == assoc.coach_id).first()
        if coach:
            coach_user = db.query(User).filter(User.id == coach.user_id).first()
            if coach_user:
                coaches.append({
                    "coach_id": coach.id,
                    "name": coach_user.name,
                    "specialty": coach.specialty,
                    "year": assoc.year,
                    "is_primary": assoc.is_primary,
                })

    detail = StudentDetailOut(
        id=student.id,
        name=student.name,
        gender=student.gender,
        birth_date=student.birth_date,
        group_name=student.group_name,
        enrollment_year=student.enrollment_year,
        parent_id=student.parent_id,
        status=student.status,
        created_at=student.created_at,
        parent_name=parent_name,
        parent_phone=parent_phone,
        parent_relationship=parent_relationship,
        coaches=coaches,
    )
    return success_response(data=detail.model_dump())


@router.post("")
def create_student(body: StudentCreate, current_user: User = Depends(require_role("coach")), db: Session = Depends(get_db)):
    coach = get_coach_for_user(current_user, db)

    parent_id = None
    if body.parent_user_id:
        parent = db.query(Parent).filter(Parent.user_id == body.parent_user_id).first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response("指定家长不存在"),
            )
        parent_id = parent.id

    student = Student(
        name=body.name,
        gender=body.gender,
        birth_date=body.birth_date,
        group_name=body.group_name,
        enrollment_year=body.enrollment_year,
        parent_id=parent_id,
        status="active",
    )
    db.add(student)
    db.flush()

    association = CoachStudent(
        coach_id=coach.id,
        student_id=student.id,
        year=body.enrollment_year,
        is_primary=True,
    )
    db.add(association)
    db.commit()
    db.refresh(student)
    return success_response(data=StudentOut.model_validate(student).model_dump(), message="创建学员成功")


@router.put("/{student_id}")
def update_student(
    student_id: int,
    body: StudentCreate,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    if not check_student_access(current_user, student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权操作该学员"),
        )
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("学员不存在"),
        )

    student.name = body.name
    student.gender = body.gender
    student.birth_date = body.birth_date
    student.group_name = body.group_name
    student.enrollment_year = body.enrollment_year

    if body.parent_user_id:
        parent = db.query(Parent).filter(Parent.user_id == body.parent_user_id).first()
        if parent:
            student.parent_id = parent.id

    db.commit()
    db.refresh(student)
    return success_response(data=StudentOut.model_validate(student).model_dump(), message="更新学员成功")
