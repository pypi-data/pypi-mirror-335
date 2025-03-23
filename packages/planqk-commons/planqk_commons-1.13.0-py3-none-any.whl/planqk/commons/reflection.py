import importlib
import inspect
from typing import Callable


def resolve_function(entrypoint: str) -> Callable:
    module_path, func_name = entrypoint.split(':')

    # import the module dynamically
    module = importlib.import_module(module_path)

    func = getattr(module, func_name)

    return func


def resolve_signature(entrypoint: str) -> inspect.Signature:
    func = resolve_function(entrypoint)

    signature = inspect.signature(func)

    return signature
