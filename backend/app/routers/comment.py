from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach
from app.models.comment import MonthlyComment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut, CommentConflictOut
from app.schemas.response import success_response, error_response
from app.middleware.auth import (
    get_current_user,
    get_coach_for_user,
    check_student_access,
    require_role,
)

router = APIRouter(prefix="/api/comments", tags=["月度评语"])


@router.post("")
def create_comment(
    body: CommentCreate,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    coach = get_coach_for_user(current_user, db)
    if not check_student_access(current_user, body.student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("无权为该学员添加评语"),
        )

    existing = db.query(MonthlyComment).filter(
        MonthlyComment.student_id == body.student_id,
        MonthlyComment.coach_id == coach.id,
        MonthlyComment.month == body.month,
        MonthlyComment.year == body.year,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response("该月评语已存在，请使用更新接口"),
        )

    comment = MonthlyComment(
        student_id=body.student_id,
        coach_id=coach.id,
        month=body.month,
        year=body.year,
        content=body.content,
        version=1,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    result = CommentOut.model_validate(comment).model_dump()
    result["coach_name"] = current_user.name
    return success_response(data=result, message="评语创建成功")


@router.put("/{comment_id}")
def update_comment(
    comment_id: int,
    body: CommentUpdate,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    coach = get_coach_for_user(current_user, db)
    comment = db.query(MonthlyComment).filter(MonthlyComment.id == comment_id).first()
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("评语不存在"),
        )
    if comment.coach_id != coach.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("只能修改自己的评语"),
        )

    if not body.force and comment.version != body.version:
        conflict = CommentConflictOut(
            current_version=comment.version,
            current_content=comment.content,
            your_version=body.version,
            your_content=body.content,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=success_response(
                data=conflict.model_dump(),
                message="版本冲突，数据已被其他人修改",
            ),
        )

    comment.content = body.content
    comment.version += 1
    db.commit()
    db.refresh(comment)

    result = CommentOut.model_validate(comment).model_dump()
    result["coach_name"] = current_user.name
    return success_response(data=result, message="评语更新成功")


@router.get("/student/{student_id}")
def list_comments_for_student(
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
    query = db.query(MonthlyComment).filter(MonthlyComment.student_id == student_id)
    if year:
        query = query.filter(MonthlyComment.year == year)
    comments = query.order_by(MonthlyComment.year, MonthlyComment.month).all()

    result = []
    for c in comments:
        coach_user = db.query(User).join(Coach, Coach.user_id == User.id).filter(Coach.id == c.coach_id).first()
        item = CommentOut.model_validate(c).model_dump()
        item["coach_name"] = coach_user.name if coach_user else "未知"
        result.append(item)
    return success_response(data=result)


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(require_role("coach")),
    db: Session = Depends(get_db),
):
    coach = get_coach_for_user(current_user, db)
    comment = db.query(MonthlyComment).filter(MonthlyComment.id == comment_id).first()
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("评语不存在"),
        )
    if comment.coach_id != coach.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("只能删除自己的评语"),
        )
    db.delete(comment)
    db.commit()
    return success_response(message="评语已删除")
