import json
import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from maleo_core.models import BaseSchemas

#* Create a specific logger for the exception middleware
exception_middleware_logger = logging.getLogger("exception_middleware")
exception_middleware_logger.setLevel(logging.ERROR)

#* Configure logging format (with logger name)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#* Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

#* Attach the handler to the logger
exception_middleware_logger.addHandler(console_handler)

class ExceptionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request:Request, call_next):
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.client.host
        try:
            return await call_next(request)
        except Exception as e:
            error_details = {
                "error": str(e),
                "traceback": traceback.format_exc().split("\n"),  #* Get full traceback
                "client_ip": client_ip,
                "method": request.method,
                "url": request.url.path,
                "headers": dict(request.headers),
            }
            exception_middleware_logger.critical("Exception occurred:\n%s", json.dumps(error_details, indent=4))  #* Log structured error
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