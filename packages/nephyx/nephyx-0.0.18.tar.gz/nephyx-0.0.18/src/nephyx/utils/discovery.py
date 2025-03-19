import importlib
import os
from pathlib import Path
import sys

from nephyx.utils.pyprojext import load_pyproject_config


def discover_root_module(app_dir=None):
    config = load_pyproject_config()
    project_name = config.get("project").get("name")

    try:
        # Check if the module exists
        spec = importlib.util.find_spec(project_name)
        if spec:
            return project_name
    except Exception as e:
        raise Exception("Could not find a Nephyx application.") from e


def discover_domain_modules(root_module):
    module_path = f"{root_module}.setup"
    module = importlib.import_module(module_path)
    return [f"{root_module}.{domain}" for domain in module.DOMAINS]


def discover_routers(domain_modules):
    for module in domain_modules:
        importlib.import_module(f"{module}.router")
