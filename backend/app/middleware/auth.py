from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach, Parent
from app.models.student import CoachStudent, Student
from app.schemas.response import error_response
from app.utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("无效的认证凭据", code=1),
        )
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("无效的认证凭据", code=1),
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("用户不存在", code=1),
        )
    return user


def require_role(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response("权限不足", code=1),
            )
        return current_user

    return role_checker


def get_coach_for_user(current_user: User, db: Session) -> Coach:
    coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
    if coach is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("非教练账号", code=1),
        )
    return coach


def get_parent_for_user(current_user: User, db: Session) -> Parent:
    parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("非家长账号", code=1),
        )
    return parent


def get_accessible_student_ids(current_user: User, db: Session) -> list[int]:
    if current_user.role == "coach":
        coach = get_coach_for_user(current_user, db)
        associations = db.query(CoachStudent).filter(CoachStudent.coach_id == coach.id).all()
        return [a.student_id for a in associations]
    elif current_user.role == "parent":
        parent = get_parent_for_user(current_user, db)
        students = db.query(Student).filter(Student.parent_id == parent.id).all()
        return [s.id for s in students]
    return []


def check_student_access(current_user: User, student_id: int, db: Session) -> bool:
    accessible_ids = get_accessible_student_ids(current_user, db)
    return student_id in accessible_ids
