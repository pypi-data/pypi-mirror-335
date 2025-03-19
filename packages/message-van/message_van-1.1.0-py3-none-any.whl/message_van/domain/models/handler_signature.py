from typing import Callable

from pydantic import BaseModel


from . import MessageHandlerType


class MessageHandlerSignature(BaseModel):
    message_class_name: str
    message_handler: Callable
    type: MessageHandlerType
