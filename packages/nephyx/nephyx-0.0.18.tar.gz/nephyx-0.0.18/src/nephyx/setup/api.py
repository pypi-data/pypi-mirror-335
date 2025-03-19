from enum import Enum

from fastapi import FastAPI


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class Endpoint:
    def __init__(self, method, path, func):
        self.method = method
        self.path = path
        self.func = func


    def inject(self, app: FastAPI):
        app.add_api_route(
            self.path,
            self.func,
            methods=[str(self.method)]
        )
