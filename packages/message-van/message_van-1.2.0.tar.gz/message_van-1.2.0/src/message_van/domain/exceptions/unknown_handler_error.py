_MSG_TEMPLATE = "No handler registered for {type}."


class UnknownHandlerError(Exception):
    def __init__(self, handler_type):
        self.handler_type = handler_type

        msg = _MSG_TEMPLATE.format(type=handler_type)

        super().__init__(msg)
