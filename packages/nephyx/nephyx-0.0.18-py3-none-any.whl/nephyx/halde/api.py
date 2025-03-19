from typing import Generator
from fastapi import FastAPI
from fastapi.security import HTTPBasic


from nephyx.core.settings import BaseSettings
from nephyx.router import NephyxApiRouter


class NephyxApi:
    def __init__(self, settings_cls: type[BaseSettings] = BaseSettings):
        self.settings = settings_cls()
        self.fastapi_app = FastAPI()

        self._setup_basic_auth()
    def _setup_basic_auth(self):
        self.fastapi_app.state.basic_auth = HTTPBasic()