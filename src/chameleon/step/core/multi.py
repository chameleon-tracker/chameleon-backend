import typing

from chameleon.step.core import core
from chameleon.step.core import context as ctx


DEFAULT_SUFFIX = "_default"

__all__ = ("multi_processor_steps", "StepHandlerMulti", "StepsDefinitionDict")

StepHandlerMulti = (
    core.StepHandlerProtocol
    | typing.Sequence[core.StepHandlerProtocol]
    | typing.Mapping[str, core.StepHandlerProtocol]
)


class StepsDefinitionDict(typing.TypedDict, total=False):
    fill_request_info: StepHandlerMulti | None
    fill_request_info_default: StepHandlerMulti | None
    check_authenticated: StepHandlerMulti | None
    check_authenticated_default: StepHandlerMulti | None
    check_headers: StepHandlerMulti | None
    check_headers_default: StepHandlerMulti | None
    check_access_pre_read: StepHandlerMulti | None
    check_access_pre_read_default: StepHandlerMulti | None
    extract_body: StepHandlerMulti | None
    extract_body_default: StepHandlerMulti | None
    decrypt: StepHandlerMulti | None
    decrypt_default: StepHandlerMulti | None
    deserialize: StepHandlerMulti | None
    deserialize_default: StepHandlerMulti | None
    validate_input: StepHandlerMulti | None
    validate_input_default: StepHandlerMulti | None
    check_access_post_read: StepHandlerMulti | None
    check_access_post_read_default: StepHandlerMulti | None
    map_input: StepHandlerMulti | None
    map_input_default: StepHandlerMulti | None
    business: StepHandlerMulti | None
    business_default: StepHandlerMulti | None
    map_output: StepHandlerMulti | None
    map_output_default: StepHandlerMulti | None
    exception_handler: StepHandlerMulti | None
    exception_handler_default: StepHandlerMulti | None
    serialize: StepHandlerMulti | None
    serialize_default: StepHandlerMulti | None
    encrypt: StepHandlerMulti | None
    encrypt_default: StepHandlerMulti | None
    response_headers: StepHandlerMulti | None
    response_headers_default: StepHandlerMulti | None
    create_response: StepHandlerMulti | None
    create_response_default: StepHandlerMulti | None


class StepsDefinitionInternal(typing.TypedDict, total=False):
    fill_request_info: core.StepHandlerProtocol | None
    check_authenticated: core.StepHandlerProtocol | None
    check_headers: core.StepHandlerProtocol | None
    check_access_pre_read: core.StepHandlerProtocol | None
    extract_body: core.StepHandlerProtocol | None
    decrypt: core.StepHandlerProtocol | None
    deserialize: core.StepHandlerProtocol | None
    validate_input: core.StepHandlerProtocol | None
    check_access_post_read: core.StepHandlerProtocol | None
    map_input: core.StepHandlerProtocol | None
    business: core.StepHandlerProtocol | None
    map_output: core.StepHandlerProtocol | None
    exception_handler: core.StepHandlerProtocol | None
    serialize: core.StepHandlerProtocol | None
    encrypt: core.StepHandlerProtocol | None
    response_headers: core.StepHandlerProtocol | None
    create_response: core.StepHandlerProtocol | None


async def noop_step(context: ctx.StepContext):
    ...


def multi_dict_step(
    default_handler: core.StepHandlerProtocol | None,
    steps_by_name: typing.Mapping[str, core.StepHandlerProtocol],
) -> core.StepHandlerProtocol:
    if not steps_by_name:
        return default_handler

    async def multi_dict_handler(context: ctx.StepContext) -> bool:
        current_step = context.current_step
        handler = steps_by_name.get(current_step)

        if handler is None:
            handled = False
        else:
            handled = bool(await handler(context))

        if not handled and default_handler is not None:
            handled = bool(await default_handler(context))

        return handled

    return multi_dict_handler


def list_step(
    steps: typing.Sequence[core.StepHandlerProtocol],
) -> core.StepHandlerProtocol:
    steps = tuple(filter(lambda step: step is not None, steps))

    if len(steps) == 0:
        return noop_step

    if len(steps) == 1:
        return steps[0]

    async def list_handler(context: ctx.StepContext):
        for step in steps:
            if step is not None:
                await step(context)

    return list_handler


def ensure_single_step(
    key: str,
    value: StepHandlerMulti,
    defaults: typing.MutableMapping[str, typing.Any] | None = None,
) -> core.StepHandlerProtocol:
    if isinstance(value, typing.Sequence):
        return list_step(value)

    if isinstance(value, typing.Mapping):
        if defaults:
            default_handler = defaults.pop(key + DEFAULT_SUFFIX, None)
        else:
            default_handler = None
        return multi_dict_step(default_handler, value)

    return value


def multi_processor_steps(
    **kwargs: typing.Unpack[StepsDefinitionDict],
) -> core.UrlHandlerSteps:
    defaults: StepsDefinitionDict = {}

    # Extract all default handlers from kwargs to defaults dict
    for key in list(kwargs.keys()):
        if key.endswith(DEFAULT_SUFFIX):
            defaults[key] = kwargs.pop(key)

    # Ensure all normal handlers are single function (with defaults)
    result: StepsDefinitionInternal = {
        key: ensure_single_step(key, value, defaults) for key, value in kwargs.items()
    }

    # Move
    for key, value in defaults.items():
        modified_key = key[: -len(DEFAULT_SUFFIX)]
        if modified_key not in result:
            result[modified_key] = ensure_single_step(modified_key, value, None)

    for key, value in list(result.items()):
        if value is None:
            del result[key]

    return core.UrlHandlerSteps(**result)
