import dataclasses
import enum
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


class StepSuffix(enum.Enum):
    DEFAULT = "default"
    PRE = "pre"
    POST = "post"


STEP_SUFFIXES = (StepSuffix.PRE.value, StepSuffix.DEFAULT.value, StepSuffix.POST.value)
allowed_steps: abc.Set[str] = {
    field.name for field in dataclasses.fields(core.UrlHandlerSteps)
}


class StepsDefinitionDict(typing.TypedDict, total=False):
    fill_request_info_pre: StepHandlerMulti | None = None
    fill_request_info: StepHandlerMulti | None = None
    fill_request_info_default: StepHandlerMulti | None = None
    fill_request_info_post: StepHandlerMulti | None = None
    check_authenticated_pre: StepHandlerMulti | None = None
    check_authenticated: StepHandlerMulti | None = None
    check_authenticated_default: StepHandlerMulti | None = None
    check_authenticated_post: StepHandlerMulti | None = None
    check_headers_pre: StepHandlerMulti | None = None
    check_headers: StepHandlerMulti | None = None
    check_headers_default: StepHandlerMulti | None = None
    check_headers_post: StepHandlerMulti | None = None
    check_access_pre_read_pre: StepHandlerMulti | None = None
    check_access_pre_read: StepHandlerMulti | None = None
    check_access_pre_read_default: StepHandlerMulti | None = None
    check_access_pre_read_post: StepHandlerMulti | None = None
    extract_body_pre: StepHandlerMulti | None = None
    extract_body: StepHandlerMulti | None = None
    extract_body_default: StepHandlerMulti | None = None
    extract_body_post: StepHandlerMulti | None = None
    decrypt_pre: StepHandlerMulti | None = None
    decrypt: StepHandlerMulti | None = None
    decrypt_default: StepHandlerMulti | None = None
    decrypt_post: StepHandlerMulti | None = None
    deserialize_pre: StepHandlerMulti | None = None
    deserialize: StepHandlerMulti | None = None
    deserialize_default: StepHandlerMulti | None = None
    deserialize_post: StepHandlerMulti | None = None
    validate_input_pre: StepHandlerMulti | None = None
    validate_input: StepHandlerMulti | None = None
    validate_input_default: StepHandlerMulti | None = None
    validate_input_post: StepHandlerMulti | None = None
    check_access_post_read_pre: StepHandlerMulti | None = None
    check_access_post_read: StepHandlerMulti | None = None
    check_access_post_read_default: StepHandlerMulti | None = None
    check_access_post_read_post: StepHandlerMulti | None = None
    map_input_pre: StepHandlerMulti | None = None
    map_input: StepHandlerMulti | None = None
    map_input_default: StepHandlerMulti | None = None
    map_input_post: StepHandlerMulti | None = None
    business_pre: StepHandlerMulti | None = None
    business: StepHandlerMulti | None = None
    business_default: StepHandlerMulti | None = None
    business_post: StepHandlerMulti | None = None
    map_output_pre: StepHandlerMulti | None = None
    map_output: StepHandlerMulti | None = None
    map_output_default: StepHandlerMulti | None = None
    map_output_post: StepHandlerMulti | None = None
    exception_handler_pre: StepHandlerMulti | None = None
    exception_handler: StepHandlerMulti | None = None
    exception_handler_default: StepHandlerMulti | None = None
    exception_handler_post: StepHandlerMulti | None = None
    serialize_pre: StepHandlerMulti | None = None
    serialize: StepHandlerMulti | None = None
    serialize_default: StepHandlerMulti | None = None
    serialize_post: StepHandlerMulti | None = None
    encrypt_pre: StepHandlerMulti | None = None
    encrypt: StepHandlerMulti | None = None
    encrypt_default: StepHandlerMulti | None = None
    encrypt_post: StepHandlerMulti | None = None
    response_headers_pre: StepHandlerMulti | None = None
    response_headers: StepHandlerMulti | None = None
    response_headers_default: StepHandlerMulti | None = None
    response_headers_post: StepHandlerMulti | None = None
    create_response_pre: StepHandlerMulti | None = None
    create_response: StepHandlerMulti | None = None
    create_response_default: StepHandlerMulti | None = None
    create_response_post: StepHandlerMulti | None = None


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
    filtered_steps: tuple[core.StepHandlerProtocol, ...]
    filtered_steps = tuple(step for step in steps if step is not None)

    if not filtered_steps:
        return None

    if len(filtered_steps) == 1:
        return filtered_steps[0]

    async def list_handler(context: ctx.StepContext):
        result = False
        for step in filtered_steps:  # pylint disable: consider-using-any-or-all
            result = await step(context) or result
        return result

    return list_handler


def make_single_step(
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

    return None


def ensure_single_step(
    step_base: StepHandlerMulti | None,
    step_default: StepHandlerMulti | None,
    step_pre: StepHandlerMulti | None,
    step_post: StepHandlerMulti | None,
) -> core.StepHandlerProtocol | None:
    single_default = make_single_step(step_definition=step_default, step_default=None)
    single_base = make_single_step(
        step_definition=step_base, step_default=single_default
    )
    base_single = single_base or single_default

    if base_single is None:
        return None

    single_pre = make_single_step(step_definition=step_pre, step_default=None)
    single_post = make_single_step(step_definition=step_post, step_default=None)

    return list_step([single_pre, base_single, single_post])


def is_step_handler_multi(value):
    if isinstance(value, core.StepHandlerProtocol):
        return True
    if isinstance(value, abc.Mapping):
        keys = all(isinstance(element, str) for element in value.keys())

        values = all(
            isinstance(element, core.StepHandlerProtocol) for element in value.values()
        )

        keys_allowed = all(element in allowed_steps for element in value.keys())

        return keys and values and keys_allowed

    if isinstance(value, abc.Sequence):
        return all(isinstance(element, core.StepHandlerProtocol) for element in value)

    raise ValueError(f"Unsupported type for value: {type(value)!r}")


def split_steps(
    *,
    defined_steps: StepsDefinitionDict,
    base_steps: abc.MutableMapping[str, StepHandlerMulti | None],
    default_steps: abc.MutableMapping[str, StepHandlerMulti | None],
    pre_steps: abc.MutableMapping[str, StepHandlerMulti | None],
    post_steps: abc.MutableMapping[str, StepHandlerMulti | None],
):
    steps: abc.Mapping[str, abc.MutableMapping[str, StepHandlerMulti | None]]

    steps = {
        "": base_steps,
        StepSuffix.DEFAULT.value: default_steps,
        StepSuffix.PRE.value: pre_steps,
        StepSuffix.POST.value: post_steps,
    }

    name: str
    step: StepHandlerMulti | None

    for name, step in defined_steps.items():  # type: ignore[assignment]
        if step is None:
            continue

        if not is_step_handler_multi(step):
            raise TypeError(
                f"Step handler for `{name}` doesn't implement StepHandlerMulti or None"
            )
        suffix: str
        if name.endswith(STEP_SUFFIXES):
            step_name, suffix = name.rsplit("_", 1)
            if suffix not in STEP_SUFFIXES:
                raise KeyError(f"Step suffix `{suffix}` is not allowed")
        else:
            step_name = name
            suffix = ""

        if step_name not in allowed_steps:
            raise KeyError(f"Step `{step_name}` is not allowed")

        steps[suffix][step_name] = step


def prepare_multi_handler_steps(
    defined_steps: StepsDefinitionDict,
) -> abc.Mapping[str, core.StepHandlerProtocol]:
    base_steps: abc.MutableMapping[str, StepHandlerMulti | None] = {}
    default_steps: abc.MutableMapping[str, StepHandlerMulti | None] = {}
    pre_steps: abc.MutableMapping[str, StepHandlerMulti | None] = {}
    post_steps: abc.MutableMapping[str, StepHandlerMulti | None] = {}

    split_steps(
        defined_steps=defined_steps,
        base_steps=base_steps,
        default_steps=default_steps,
        pre_steps=pre_steps,
        post_steps=post_steps,
    )

    # Ensure all normal handlers become single function (with defaults)
    result: dict[str, core.StepHandlerProtocol | None] = {}

    for step in allowed_steps:
        # noinspection PyTypeChecker
        result[step] = ensure_single_step(
            step_base=base_steps.get(step),
            step_default=default_steps.get(step),
            step_pre=pre_steps.get(step),
            step_post=post_steps.get(step),
        )

    return clean_values(result)


def multi_processor_steps(
    **kwargs: typing.Unpack[StepsDefinitionDict],
) -> core.UrlHandlerSteps:
    # noinspection PyTypeChecker
    # PyCharm can't properly recognize this ATM
    result = prepare_multi_handler_steps(kwargs)
    return core.UrlHandlerSteps(**result)
