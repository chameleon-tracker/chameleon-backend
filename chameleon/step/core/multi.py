import dataclasses
import typing
from collections import abc

from chameleon.step.core import context as ctx
from chameleon.step.core import core

__all__ = ("multi_processor_steps", "StepHandlerMulti", "StepsDefinitionDict")

StepHandlerMulti = (
    core.StepHandlerProtocol
    | abc.Sequence[core.StepHandlerProtocol | None]
    | abc.Mapping[str, core.StepHandlerProtocol | None]
)

DEFAULT_SUFFIX = "_default"
PRE_SUFFIX = "_pre"
POST_SUFFIX = "_post"


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


T = typing.TypeVar("T")


def clean_values(source: abc.Mapping[str, T | None]) -> abc.Mapping[str, T]:
    return {key: value for key, value in source.items() if value is not None}


def multi_dict_step(
    default_handler: core.StepHandlerProtocol | None,
    steps_by_name: abc.Mapping[str, core.StepHandlerProtocol | None],
) -> core.StepHandlerProtocol | None:
    steps = clean_values(steps_by_name)

    if not steps:
        return default_handler

    async def multi_dict_handler(context: ctx.StepContext) -> bool:
        current_step = context.current_step
        handler = steps.get(current_step)

        if handler is None:
            handled = False
        else:
            handled = bool(await handler(context))

        if not handled and default_handler is not None:
            handled = bool(await default_handler(context))

        return handled

    return multi_dict_handler


def list_step(
    steps: abc.Sequence[core.StepHandlerProtocol | None],
) -> core.StepHandlerProtocol | None:
    steps = tuple(filter(lambda step: step is not None, steps))

    if len(steps) == 0:
        return None

    if len(steps) == 1:
        return steps[0]

    async def list_handler(context: ctx.StepContext):
        for step in steps:
            if step is not None:
                await step(context)

    return list_handler


def make_single_step(
    key: str,
    step_definition: StepHandlerMulti | None,
    step_default: core.StepHandlerProtocol | None,
) -> core.StepHandlerProtocol | None:
    if step_definition is None:
        return step_default

    # step has been defined explicitly,ignoring default
    if isinstance(step_definition, core.StepHandlerProtocol):
        return step_definition

    # step is a sequence, ignoring default
    if isinstance(step_definition, abc.Sequence):
        return list_step(step_definition)

    # step is mapping, e.g. exception handler using default
    if isinstance(step_definition, abc.Mapping):
        return multi_dict_step(step_default, step_definition)

    raise ValueError(f"Step {key} has unknown type: {step_definition!r}")


def ensure_single_step(
    key: str,
    step_definition: StepHandlerMulti | None,
    defaults: abc.MutableMapping[str, typing.Any],
) -> core.StepHandlerProtocol | None:
    key_default = key + DEFAULT_SUFFIX
    step_default = make_single_step(key_default, defaults.pop(key_default, None), None)
    step = make_single_step(key_default, step_definition, step_default)

    return step or step_default


def prepare_multi_handler_steps(
    kwargs: StepsDefinitionDict,
) -> abc.Mapping[str, core.StepHandlerProtocol]:
    defaults: abc.MutableMapping[str, core.StepHandlerProtocol] = {}

    # Extract all default handlers from kwargs to defaults dict
    for key in list(kwargs.keys()):
        if key.endswith(DEFAULT_SUFFIX):
            defaults[key] = kwargs.pop(key)

    # Ensure all normal handlers become single function (with defaults)
    result: dict[str, core.StepHandlerProtocol | None] = {}

    for field in dataclasses.fields(core.UrlHandlerSteps):
        key = field.name
        # noinspection PyTypeChecker
        step = ensure_single_step(key, kwargs.pop(key, None), defaults)
        result[key] = step

    if kwargs or defaults:
        common = {**kwargs, **defaults}
        raise ValueError(f"Found unsupported keys in kwargs: {tuple(common.keys())}")

    return clean_values(result)


def multi_processor_steps(
    **kwargs: typing.Unpack[StepsDefinitionDict],
) -> core.UrlHandlerSteps:
    # noinspection PyTypeChecker
    # PyCharm can't properly recognize this ATM
    result = prepare_multi_handler_steps(kwargs)
    return core.UrlHandlerSteps(**result)
