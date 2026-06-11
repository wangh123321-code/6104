from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    code: int = 0
    data: Optional[T] = None
    message: str = "success"


def success_response(data=None, message: str = "success") -> dict:
    return {"code": 0, "data": data, "message": message}


def error_response(message: str, code: int = 1) -> dict:
    return {"code": code, "data": None, "message": message}
