from datetime import datetime, date
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_serializer, field_validator
from typing import Literal, Optional, Any
from uuid import UUID
from .payload import Pagination

class Get(BaseModel):
    id:int
    uuid:UUID
    created_at:datetime
    updated_at:datetime
    is_active:bool
    is_deleted:bool

    @field_validator('*', mode="before")
    def set_none(cls, v):
        if isinstance(v, str) and (v == "" or len(v) == 0):
            return None
        return v

    @field_serializer('*')
    def serialize_values(self, v):
        if isinstance(v, datetime) or isinstance(v, date):
            return v.isoformat()
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes=True

class SingleData(BaseModel):
    data:Optional[Any] = None

class MultipleData(BaseModel):
    data:list[Any] = []
    pagination:Pagination

class Authorization(BaseModel):
    authorized:Literal[False, True]
    response:Optional[JSONResponse] = None
    token:Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class Controller(BaseModel):
    success:Literal[True, False]
    response:Optional[JSONResponse]

    class Config:
        arbitrary_types_allowed=True