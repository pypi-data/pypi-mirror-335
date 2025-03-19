from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from maleo_core.models import BaseSchemas

async def validation_exception_handler(request:Request, exc:RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=BaseSchemas.Response.ValidationError(other=exc.errors()).model_dump())