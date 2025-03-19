from collections import defaultdict

from message_van.domain.exceptions import UnknownHandlerError
from message_van.domain.models import (
    Command,
    CommandHandler,
    Event,
    EventHandler,
    MessageHandlerSignature,
    MessageHandlerType,
    Message,
)


class MessageHandlers:
    _command_handlers: dict[str, CommandHandler]
    _event_handlers: dict[str, list[EventHandler]]

    def __init__(self):
        self._command_handlers = {}
        self._event_handlers = defaultdict(list)

    def get_handler_for_command(self, command: Command) -> CommandHandler:
        command_name = _get_message_name(command)

        return self._get_handler_for_command(command_name)

    def _get_handler_for_command(self, command_name: str) -> CommandHandler:
        try:
            return self._command_handlers[command_name]
        except KeyError:
            raise UnknownHandlerError(command_name)

    def get_handlers_for_event(self, event: Event) -> list[EventHandler]:
        event_name = _get_message_name(event)

        return self._get_handlers_for_event(event_name)

    def _get_handlers_for_event(self, event_name: str) -> list[EventHandler]:
        try:
            return self._event_handlers[event_name]
        except KeyError:
            raise UnknownHandlerError(event_name)

    def register(self, signature: MessageHandlerSignature) -> None:
        type_ = signature.type
        class_name = signature.message_class_name
        handler = signature.message_handler

        if type_ == MessageHandlerType.COMMAND:
            self._register_command(class_name, handler)
        else:
            self._register_event(class_name, handler)

    def _register_command(
        self,
        class_name: str,
        handler: CommandHandler,
    ) -> None:
        self._command_handlers[class_name] = handler

    def _register_event(self, class_name: str, handler: EventHandler) -> None:
        self._event_handlers[class_name].append(handler)


def _get_message_name(message: Message) -> str:
    message_class = message.__class__

    return message_class.__name__
