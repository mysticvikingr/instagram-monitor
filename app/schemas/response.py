from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    status_code: int = 200
    success: bool = True
    data: Optional[T] = None 