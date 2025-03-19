from asyncclick import group


def cli_group(*args, **kwargs):
    def decorator(func):
        async def wrapped(*func_args, **func_kwargs):
            from message_van import MessageVan  # noqa: F401

            return await func(*func_args, **func_kwargs)

        return group(*args, **kwargs)(wrapped)

    return decorator

