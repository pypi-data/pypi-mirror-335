_MSG_TEMPLATE = "Handler {handler} is already registered for {type}."


class AlreadyRegisteredHandlerError(Exception):
    def __init__(self, existing_handler, handler_type):
        self.existing_handler = existing_handler
        self.handler_type = handler_type

        msg = _MSG_TEMPLATE.format(handler=existing_handler, type=handler_type)

        super().__init__(msg)
