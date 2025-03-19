from message_van.adapters.models import UserConfig


def dict_to_user_config(config_dict: dict) -> UserConfig:
    return UserConfig.model_validate(config_dict)
