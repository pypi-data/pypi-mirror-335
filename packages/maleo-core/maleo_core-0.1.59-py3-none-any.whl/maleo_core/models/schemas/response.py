from typing import Literal, Optional, Any
from pydantic import BaseModel
from ..transfers.payload import Pagination

class Response:
    #* ----- ----- ----- Base ----- ----- ----- *#
    class Base(BaseModel):
        success:Literal[True, False]
        code:str
        message:str
        description:str

    #* ----- ----- ----- Derived ----- ----- ----- *#
    class Fail(Base):
        success:Literal[False] = False
        other:Optional[Any] = None

    class ServerError(Fail):
        code:str = "MAL-EXC-001"
        message:str = "Unexpected Server Error"
        description:str = "An unexpected error occurred. Please try again later or contact administrator."

    class ValidationError(Fail):
        code:str = "MAL-EXC-002"
        message:str = "Validation Error"
        description:str = "Request validation failed due to missing or invalid fields. Check other for more info."

    class NotFoundError(Fail):
        code:str = "MAL-EXC-003"
        message:str = "Not Found Error"
        description:str = "The resource you requested can not be found. Ensure your request is correct."

    class RateLimitExceeded(Fail):
        code:str = "MAL-RTL-001"
        message:str = "Rate Limit Exceeded"
        description:str = "This resource is requested too many times. Please try again later."

    class Unauthorized(Fail):
        code:str = "MAL-ATH-001"
        message:str = "Unauthorized Request"

    class Forbidden(Fail):
        code:str = "MAL-ATH-002"
        message:str = "Forbidden Request"

    class SingleData(Base):
        success:Literal[True] = True
        data:Any
        other:Optional[Any] = None

    class MultipleData(Base):
        success:Literal[True] = True
        data:list[Any]
        pagination:Pagination
        other:Optional[Any] = None