from wrapt import decorator


@decorator
async def entrypoint(
    wrapped=None,
    _=None,
    args=None,
    kwargs=None,
):
    from message_van import MessageVan  # noqa F401

    return await wrapped(*args, **kwargs)


@decorator
def sync_entrypoint(
    wrapped=None,
    _=None,
    args=None,
    kwargs=None,
):
    from message_van import MessageVan  # noqa F401

    return wrapped(*args, **kwargs)
