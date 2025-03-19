from asyncio import create_task, gather
from types import TracebackType
from typing import Any

from message_van.domain.models import CommandHandler, EventHandler
from message_van.domain.models.base import Command, Event, Message

from . import UnitOfWork, MessageHandlers


class MessageVan:
    uow: UnitOfWork

    _message_handlers: MessageHandlers

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __aenter__(self) -> "MessageVan":
        self.uow = await self.unit_of_work.__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        await self.unit_of_work.__aexit__(exc_type, exc_val, exc_tb)

    async def publish(self, message: Message) -> Any | None:
        if isinstance(message, Command):
            return await self.publish_command(message)

        await self.publish_event(message)

    async def publish_command(self, command: Command) -> Any:
        handler = self._get_handler_for_command(command)

        return await handler(command, self)

    async def publish_event(self, event: Event) -> None:
        tasks = [
            create_task(handler(event, self))
            for handler in self._get_handlers_for_event(event)
        ]

        await gather(*tasks)

    def _get_handler_for_command(self, command: Command) -> CommandHandler:
        return self._message_handlers.get_handler_for_command(command)

    def _get_handlers_for_event(self, event: Event) -> list[EventHandler]:
        return self._message_handlers.get_handlers_for_event(event)


def init_handlers(message_handlers: MessageHandlers) -> None:
    MessageVan._message_handlers = message_handlers
