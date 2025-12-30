from pydantic import BaseModel
from typing import Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: dict
    
    class Config:
        from_attributes = True


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: dict
    
    class Config:
        from_attributes = True
