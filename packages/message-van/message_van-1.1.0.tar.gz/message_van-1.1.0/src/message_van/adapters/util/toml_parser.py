import sys
from types import ModuleType


MIN_PYTHON_VERSION_FOR_TOMLI = (3, 11)


def get_toml_parser() -> ModuleType:
    if _is_python_version_compatible_with_tomllib():
        import tomllib
    else:
        import tomli as tomllib

    return tomllib


def _is_python_version_compatible_with_tomllib() -> bool:
    current_python_version = sys.version_info

    return current_python_version >= MIN_PYTHON_VERSION_FOR_TOMLI
