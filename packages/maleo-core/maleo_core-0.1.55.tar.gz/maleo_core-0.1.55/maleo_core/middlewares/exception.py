import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from maleo_core.models import BaseSchemas

class ExceptionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request:Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logging.critical(e)
            return JSONResponse(content=BaseSchemas.Response.ServerError().model_dump(), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def add_exception_middleware(app:FastAPI) -> None:
    """
    Adds Exception middleware to the FastAPI application.

    This middleware try to process request and if fail, will return proper error response.

    Args:
        app: FastAPI
            The FastAPI application instance to which the middleware will be added.

    Returns:
        None: The function modifies the FastAPI app by adding Exception middleware.

    Example:
    ```python
    add_exception_middleware(app=app)
    ```
    """
    app.add_middleware(ExceptionMiddleware)