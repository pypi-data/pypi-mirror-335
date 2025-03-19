from pathlib import Path


def load_handlers():
    from message_van.adapters import SignatureAdapter
    from message_van.domain.models import (
        MessageHandlers,
    )

    message_handlers = MessageHandlers()

    path = _get_handlers_path()
    signatures = SignatureAdapter(path)

    for signature in signatures.list():
        message_handlers.register(signature)

    return message_handlers


def _get_handlers_path() -> Path:
    from message_van.adapters import ConfigAdapter

    pyproject_path = Path("pyproject.toml")
    config_adapter = ConfigAdapter(pyproject_path)

    config = config_adapter.get()

    return config.handlers_path
