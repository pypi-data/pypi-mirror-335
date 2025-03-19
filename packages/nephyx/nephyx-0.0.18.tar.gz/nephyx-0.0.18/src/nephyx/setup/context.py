from nephyx.setup.api import Endpoint


class ApplicationContext:

    def __init__(self):
        self.endpoints = []

    def register_endpoint(self, method, path, func):
        endpoint = Endpoint(method, path, func)
        self.endpoints.append(endpoint)


__context = ApplicationContext()


def get_context():
    return __context
