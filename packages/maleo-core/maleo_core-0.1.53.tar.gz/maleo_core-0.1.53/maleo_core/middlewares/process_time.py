import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request:Request, call_next):
        start_time = time.perf_counter() #* Record the start time
        response = await call_next(request) #* Process the request and get the response
        process_time = time.perf_counter() - start_time #* Calculate the process time
        response.headers["X-Process-Time"] = str(process_time) #* Add the process time to the response headers
        return response

def add_process_time_middleware(app:FastAPI) -> None:
    """
    Adds Process Time middleware to the FastAPI application.

    This middleware always return process time of the request in the response header.

    Args:
        app: FastAPI
            The FastAPI application instance to which the middleware will be added.

    Returns:
        None: The function modifies the FastAPI app by adding Process Time middleware.

    Example:
    ```python
    add_process_time_middleware(app=app)
    ```
    """
    app.add_middleware(ProcessTimeMiddleware)