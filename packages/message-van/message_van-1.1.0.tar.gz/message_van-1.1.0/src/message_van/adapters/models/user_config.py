from pathlib import Path

from pydantic import BaseModel, Field

from message_van.config import HANDLERS_PATH_KEY


class UserConfig(BaseModel):
    handlers_path: Path = Field(alias=HANDLERS_PATH_KEY)
