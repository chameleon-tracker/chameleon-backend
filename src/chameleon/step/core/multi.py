import typing

from chameleon.step import core

DEFAULT_SUFFIX = "_default"

__all__ = ("multi_processor_steps",)


def multi_dict_step(
    default_handler: core.StepHandlerProtocol,
    steps_by_name: typing.Mapping[str, core.StepHandlerProtocol],
) -> core.StepHandlerProtocol:
    async def multi_dict_handler(context: core.StepContext) -> bool:
        current_step = context.current_step
        handler = steps_by_name.get(current_step)

        if handler is None:
            handled = False
        else:
            handled = await handler(context)

        if not handled and default_handler is not None:
            return await default_handler(context)

        return False

    return multi_dict_handler


def list_step(
    steps: typing.Sequence[core.StepHandlerProtocol],
) -> core.StepHandlerProtocol:
    steps = tuple(filter(lambda step: step is not None, steps))

    if len(steps) == 0:
        return core.noop_step

    if len(steps) == 1:
        return steps[0]

    async def list_handler(context: core.StepContext):
        for step in steps:
            if step is not None:
                await step(context)

    return list_handler


def ensure_single_step(
    key: str,
    value: core.StepHandlerProtocol
    | typing.Mapping[str, core.StepHandlerProtocol]
    | typing.Sequence[core.StepHandlerProtocol],
    defaults: typing.MutableMapping[str, typing.Any] = None,
) -> core.StepHandlerProtocol:
    if isinstance(value, typing.Sequence):
        return list_step(value)
    elif isinstance(value, typing.Mapping):
        if defaults:
            default_handler = defaults.pop(key + DEFAULT_SUFFIX, None)
        else:
            default_handler = None
        return multi_dict_step(default_handler, value)
    else:
        return value


def multi_processor_steps(
    **kwargs: core.StepHandlerProtocol
    | typing.Mapping[str, core.StepHandlerProtocol]
    | typing.Sequence[core.StepHandlerProtocol]
) -> core.UrlHandlerSteps:
    defaults = {}

    # Extract all default handlers from kwargs to defaults dict
    for key in list(kwargs.keys()):
        if key.endswith(DEFAULT_SUFFIX):
            defaults[key] = kwargs.pop(key)

    # Ensure all normal handlers are single function (with defaults)
    result = {
        key: ensure_single_step(key, value, defaults) for key, value in kwargs.items()
    }

    # Move
    for key, value in defaults.items():
        modified_key = key[: -len(DEFAULT_SUFFIX)]
        if modified_key not in result:
            result[modified_key] = ensure_single_step(modified_key, value, None)

    keys_to_remove = set()
    for key, value in list(result.items()):
        if value is None:
            del result[key]

    return core.UrlHandlerSteps(**result)
