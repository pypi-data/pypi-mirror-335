from nephyx.setup.api import HttpMethod
from nephyx.setup.context import get_context

def get(path: str):
    def decorator(func):
        ctx = get_context()
        ctx.register_endpoint(HttpMethod.GET, path, func)

        #from fastapi.dependencies.utils import get_typed_signature
        #signature = get_typed_signature(func)
        #print(signature)

        return func
    return decorator


def post(path: str):
    def decorator(func):
        ctx = get_context()
        ctx.register_endpoint(HttpMethod.POST, path, func)
        return func
    return decorator
