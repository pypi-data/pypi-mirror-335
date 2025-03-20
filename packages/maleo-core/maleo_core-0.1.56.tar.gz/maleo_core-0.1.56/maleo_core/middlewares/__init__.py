from fastapi import FastAPI
from typing import Sequence
from maleo_core.models import BaseTransfers
from .authorization import add_authorization_middleware
from .cors import add_cors_middleware
from .exception import add_exception_middleware
from .logging import add_logging_middleware
from .process_time import add_process_time_middleware
from .rate_limit import add_rate_limit_middleware

class MiddlewareManager:
    _default_limit:int = 10
    _default_window:int = 1
    _default_allow_origins:Sequence[str] = (),
    _default_allow_methods:Sequence[str] = ("GET",),
    _default_allow_headers:Sequence[str] = (),
    _default_allow_credentials:bool = False,
    _default_expose_headers:Sequence[str] = (),
    _default_permissions:BaseTransfers.Parameter.RoutesPermissions = {}

    def __init__(self, app:FastAPI):
        self.app = app

    def add_all_middlewares(
        self,
        limit:int = _default_limit,
        window:int = _default_window,
        allow_origins:Sequence[str] = _default_allow_origins,
        allow_methods:Sequence[str] = _default_allow_methods,
        allow_headers:Sequence[str] = _default_allow_headers,
        allow_credentials:bool = _default_allow_credentials,
        expose_headers:Sequence[str] = _default_expose_headers,
        permissions:BaseTransfers.Parameter.RoutesPermissions = _default_permissions
    ):
        self.add_cors_middleware(allow_origins, allow_methods, allow_headers, allow_credentials, expose_headers)
        self.add_logging_middleware()
        self.add_rate_limit_middleware(limit=limit, window=window)
        self.add_exception_middleware()
        self.add_authorization_middleware(permissions=permissions)
        self.add_process_time_middleware()

    def add_logging_middleware(self):
        add_logging_middleware(self.app)

    def add_cors_middleware(
        self,
        allow_origins:Sequence[str] = _default_allow_origins,
        allow_methods:Sequence[str] = _default_allow_methods,
        allow_headers:Sequence[str] = _default_allow_headers,
        allow_credentials:bool = _default_allow_credentials,
        expose_headers:Sequence[str] = _default_expose_headers
    ):
        add_cors_middleware(
            self.app,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            expose_headers=expose_headers
        )

    def add_rate_limit_middleware(self, limit:int = _default_limit, window:int = _default_window):
        add_rate_limit_middleware(self.app, limit=limit, window=window)

    def add_exception_middleware(self):
        add_exception_middleware(self.app)

    def add_authorization_middleware(self, permissions:BaseTransfers.Parameter.RoutesPermissions = _default_permissions):
        add_authorization_middleware(self.app, permissions=permissions)

    def add_process_time_middleware(self):
        add_process_time_middleware(self.app)