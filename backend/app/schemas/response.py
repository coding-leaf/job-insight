from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ResponseModel(BaseModel, Generic[DataT]):
    code: int = 200
    message: str = "success"
    data: DataT | None = None


def success_response(
    data: DataT, message: str = "success", code: int = 200
) -> ResponseModel[DataT]:
    return ResponseModel(code=code, message=message, data=data)


def error_response(
    code: int, message: str, data: DataT | None = None
) -> ResponseModel[DataT]:
    return ResponseModel(code=code, message=message, data=data)
