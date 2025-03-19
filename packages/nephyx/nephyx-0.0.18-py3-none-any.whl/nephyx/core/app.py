from fastapi import FastAPI
from starlette.types import Receive, Scope, Send

from nephyx.core.settings import BaseSettings
from nephyx.db.manager import DatabaseSessionManager
from nephyx.router import NephyxApiRouter
from nephyx.setup.context import get_context
from nephyx.utils.discovery import discover_domain_modules, discover_root_module, discover_routers

class NephyxApplication:
    def __init__(self):
        self.settings = BaseSettings()  # TODO autodiscovery
        self.fastapi_app = FastAPI()
        self.db = DatabaseSessionManager(self.settings)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.fastapi_app(scope, receive, send)

    def register_endpoints(self, context):
        router = NephyxApiRouter(self)
        for endpoint in context.endpoints:
            router.add_api_route(
                endpoint.path,
                endpoint.func,
                endpoint.method.name
            )
        self.fastapi_app.include_router(router)


def get_app():
    root_module = discover_root_module()
    domain_modules = discover_domain_modules(root_module)

    context = get_context()
    app = NephyxApplication()

    discover_routers(domain_modules)
    app.register_endpoints(context)

    return app
