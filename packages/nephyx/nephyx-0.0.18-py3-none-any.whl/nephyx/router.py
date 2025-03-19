import functools
from typing import Callable, ParamSpec, TypeVar
from fastapi import APIRouter as FastApiRouter

from nephyx.core.schema import DataResponse

T = TypeVar("T")
P = ParamSpec("P")


class NephyxApiRouter(FastApiRouter):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = app

    def _inject_app_dependency(self, endpoint: Callable[P, T]) -> Callable[P, T]:
        if not self._app:
            raise RuntimeError("App dependency not set.?")

        return endpoint

    def _wrap_data_response(self, endpoint: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(endpoint)
        def wrapped(*args, **kwargs):
            response_data = endpoint(*args, **kwargs)
            print(response_data)
            return DataResponse(data=response_data)
        return wrapped

    def add_api_route(self, path: str, endpoint, method):
        wrapped_endpoint = self._inject_app_dependency(endpoint)
        wrapped_endpoint = self._wrap_data_response(wrapped_endpoint)
        super().add_api_route(path, wrapped_endpoint, methods=[method])
