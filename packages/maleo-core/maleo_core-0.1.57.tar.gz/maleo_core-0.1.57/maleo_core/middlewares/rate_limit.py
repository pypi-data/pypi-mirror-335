from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from maleo_core.models import BaseSchemas

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit:int = 10, window:int = 1):
        super().__init__(app)
        self.limit = limit
        self.window = timedelta(seconds=window)
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now()

        #* Filter requests within the window
        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if now - timestamp <= self.window]

        #* Check if the request count exceeds the limit
        if len(self.requests[client_ip]) >= self.limit:
            return JSONResponse(content=BaseSchemas.Response.RateLimitExceeded().model_dump(), status_code=status.HTTP_429_TOO_MANY_REQUESTS)

        #* Add the current request timestamp
        self.requests[client_ip].append(now)
        return await call_next(request)

def add_rate_limit_middleware(app:FastAPI, limit:int = 10, window:int = 1) -> None:
    """
    Adds Rate Limit middleware to the FastAPI application.

    This middleware limits how many request can the endpoint process within a window from a user.

    Args:
        app: FastAPI
            The FastAPI application instance to which the middleware will be added.

        limit: int
            Request count limit in a specific window of time

        window: int
            Time window for rate limiting (in seconds).

    Returns:
        None: The function modifies the FastAPI app by adding Process Time middleware.

    Example:
    ```python
    add_rate_limit_middleware(app=app, limit=10, window=1)
    ```
    """
    app.add_middleware(RateLimitMiddleware, limit=limit, window=window)