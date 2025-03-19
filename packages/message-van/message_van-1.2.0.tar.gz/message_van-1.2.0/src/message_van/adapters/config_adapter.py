from pathlib import Path

from message_van.adapters.mappers import dict_to_user_config
from message_van.adapters.models import UserConfig
from message_van.adapters.util import get_toml_parser
from message_van.config import USER_CONFIG_KEY


class ConfigAdapter:
    _parser = get_toml_parser()

    def __init__(self, config_path: Path):
        self.config_path = config_path

    def get(self) -> UserConfig:
        config_dict = self._get()

        return dict_to_user_config(config_dict)

    def _get(self) -> dict:
        pyproject_dict = self._get_pyproject_dict()

        return pyproject_dict["tool"][USER_CONFIG_KEY]

    def _get_pyproject_dict(self) -> dict:
        contents = self.config_path.read_text()

        return self._parser.loads(contents)
