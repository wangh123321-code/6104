from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Coach, Parent
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.schemas.response import success_response, error_response
from app.utils.auth import hash_password, verify_password, create_access_token
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("用户名或密码错误"),
        )
    token_data = {"user_id": user.id, "role": user.role}
    access_token = create_access_token(token_data)
    return success_response(data={"access_token": access_token, "token_type": "bearer"}, message="登录成功")


@router.post("/register")
def register(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("用户名已存在"),
        )
    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        name=body.name,
        phone=body.phone,
    )
    db.add(user)
    db.flush()

    if body.role == "coach":
        coach = Coach(user_id=user.id, specialty=body.specialty or "")
        db.add(coach)
    elif body.role == "parent":
        parent = Parent(user_id=user.id, kinship=body.kinship or "家长")
        db.add(parent)

    db.commit()
    db.refresh(user)
    return success_response(data=UserOut.model_validate(user).model_dump(), message="注册成功")


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(data=UserOut.model_validate(current_user).model_dump())
