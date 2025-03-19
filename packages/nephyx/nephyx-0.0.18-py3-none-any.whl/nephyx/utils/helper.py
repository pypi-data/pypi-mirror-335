import importlib
from typing import Any
from fastapi import FastAPI

from nephyx.utils.pyprojext import load_pyproject_config



def get_app_entrypoint(config: dict[str, Any]) -> tuple[str, str] | None:
    try:
        config_value = config.get("tool", {}).get("nephyx", {}).get("app")
        module_path, obj = config_value.split(":")
        return module_path, obj
    except (KeyError, AttributeError):
        return None


def import_app_entrypoint() -> FastAPI:  # TODO return nephyxapp
    config = load_pyproject_config()
    app_entrypoint = get_app_entrypoint(config)
    if not app_entrypoint:
        raise ValueError("Could not find app entrypoint in pyproject.toml")
    module_path, app_name = app_entrypoint
    module = importlib.import_module(module_path)
    return getattr(module, app_name)
