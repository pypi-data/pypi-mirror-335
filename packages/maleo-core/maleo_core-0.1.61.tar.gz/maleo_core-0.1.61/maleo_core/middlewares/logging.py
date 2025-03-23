import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

#* Create a specific logger for the application
logging_middleware_logger = logging.getLogger("logging_middleware_logger")
logging_middleware_logger.setLevel(logging.INFO)

#* Configure logging format (with logger name)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#* Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

#* Attach the handler to the logger
logging_middleware_logger.addHandler(console_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request:Request, call_next):
        response = await call_next(request) #* Process the request and get the response
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.client.host
        logging_middleware_logger.info(f"Request | IP: {client_ip} | Method: {request.method} | URL: {request.url} | Base URL: {request.base_url} | URL Path: {request.url.path} | Path Params: {request.path_params} | Query Params: {request.query_params} | Status: {response.status_code}")
        return response

def add_logging_middleware(app:FastAPI) -> None:
    """
    Adds Logging middleware to the FastAPI application.

    This middleware always logs any request and response.

    Args:
        app: FastAPI
            The FastAPI application instance to which the middleware will be added.

    Returns:
        None: The function modifies the FastAPI app by adding Logging middleware.

    Example:
    ```python
    add_logging_middleware(app=app)
    ```
    """
    app.add_middleware(LoggingMiddleware)