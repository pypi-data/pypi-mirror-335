import os
import importlib.util
import inspect
from collections.abc import Generator
from pathlib import Path
from typing import Any, List, Callable


from message_van.domain.models import (
    Command,
    Message,
    MessageHandlerType,
    MessageHandlerSignature,
)


class SignatureAdapter:
    def __init__(self, path: Path):
        self.path = path

    def list(self) -> Generator[MessageHandlerSignature]:
        module_paths = self.get_module_paths()
        modules = self.import_modules(module_paths)

        for func in list_modules(modules):
            if signature := get_signature(func):
                yield signature

    def get_module_paths(self) -> List[Path]:
        return [module_path for module_path in self.list_module_paths()]

    def list_module_paths(self) -> Generator[Path]:
        for root_path, file_name in self.list_file_names():
            if _is_module(file_name):
                yield root_path / Path(file_name)

    def list_file_names(self) -> Generator[tuple]:
        for root, _, file_names in os.walk(self.path):
            root_path = Path(root)

            for file_name in file_names:
                yield root_path, file_name

    def import_modules(self, module_paths: List[Path]) -> Generator:
        for file_path in module_paths:
            yield self.import_module(file_path)

    def import_module(self, file_path: str) -> Any:
        module_name = os.path.relpath(file_path, self.path).replace(
            os.sep, "."
        )[:-3]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module


def _is_module(file_name: str) -> bool:
    return file_name.endswith(".py")


def list_modules(modules: list) -> Generator[Callable]:
    for module in modules:
        for func in list_public_functions(module):
            yield func


def list_public_functions(module) -> Generator[Callable]:
    for func in _list_functions(module):
        if _is_public_function(func):
            yield func


def _list_functions(module) -> Generator[Callable]:
    for _, func in inspect.getmembers(module, inspect.isfunction):
        yield func


def _is_public_function(func: Callable) -> bool:
    name = func.__name__

    return not name.startswith("_")


def get_signature(func) -> MessageHandlerSignature:
    if param := get_message_param(func):
        return MessageHandlerSignature(
            message_class_name=get_class_name(param),
            message_handler=func,
            type=get_handler_type(param),
        )


def get_message_param(func):
    for param in list_params(func):
        if is_message_param(param):
            return param


def list_params(func) -> Generator:
    signature = inspect.signature(func)

    yield from signature.parameters.values()


def is_message_param(param):
    return issubclass(param.annotation, Message)


def get_class_name(param):
    return param.annotation.__name__


def get_handler_type(param) -> MessageHandlerType:
    if issubclass(param.annotation, Command):
        return MessageHandlerType.COMMAND

    return MessageHandlerType.EVENT
