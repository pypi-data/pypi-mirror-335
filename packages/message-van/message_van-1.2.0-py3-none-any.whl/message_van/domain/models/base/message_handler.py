from typing import TYPE_CHECKING, Any, Awaitable, Callable

from . import Message


if TYPE_CHECKING:
    from message_van.domain.models import MessageVan

    message_van_type = MessageVan
else:
    message_van_type = "MessageVan"


MessageHandler = Callable[[Message, message_van_type], Awaitable[Any | None]]
