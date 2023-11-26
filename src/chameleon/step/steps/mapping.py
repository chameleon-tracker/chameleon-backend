# Basic Mapping and Validation function generators
import dataclasses
import functools
import typing

from chameleon.step import core, registry

__all__ = ("default_mapping_steps",)


@dataclasses.dataclass(slots=True, frozen=True, kw_only=True)
class RuntimeMappingContext:
    """Internal mapping context for the handler."""

    type_id: str
    action_id: str | None
    is_input: bool
    expect_list: bool | None


def runtime_mapper_get_input(context: core.StepContext, is_input: bool):
    if is_input:
        value = context.input_raw
    else:
        value = context.output_business

    return value


def runtime_mapping_set_output(context: core.StepContext, value, is_input: bool):
    if is_input:
        context.input_business = value
    else:
        context.output_raw = value


async def mapper_step_runtime(
    context: core.StepContext, *, mapping_context: RuntimeMappingContext
):
    input_value = runtime_mapper_get_input(context, mapping_context.is_input)
    mapper_function = registry.mapper_registry.get(
        mapping_context.type_id, mapping_context.action_id
    )

    if mapper_function is None:
        return

    if mapping_context.expect_list:
        output_value = list(map(mapper_function, input_value))
    else:
        output_value = mapper_function(input_value)

    runtime_mapping_set_output(context, output_value, mapping_context.is_input)


@typing.runtime_checkable
class MapperStepProtocol(typing.Protocol):
    """Internal mapper step protocol."""

    async def __call__(
        self, context: core.StepContext, *, mapping_function: registry.ProcessorProtocol
    ):
        ...


async def mapper_step_single_input(
    context: core.StepContext, *, mapping_function: registry.ProcessorProtocol
):
    context.input_business = mapping_function(context.input_raw)


async def mapper_step_single_output(
    context: core.StepContext, *, mapping_function: registry.ProcessorProtocol
):
    context.output_raw = mapping_function(context.output_business)


async def mapper_step_list_input(
    context: core.StepContext, *, mapping_function: registry.ProcessorProtocol
):
    context.input_business = list(map(mapping_function, context.input_raw))


async def mapper_step_list_output(
    context: core.StepContext, *, mapping_function: registry.ProcessorProtocol
):
    context.output_raw = list(map(mapping_function, context.output_business))


# (is_input, expect_list) -> handler
mapping_functions: dict[tuple[bool, bool], MapperStepProtocol] = {
    (True, True): mapper_step_list_input,
    (True, False): mapper_step_single_input,
    (False, True): mapper_step_list_output,
    (False, False): mapper_step_single_output,
}


def generic_mapper_step(
    *,
    type_id: str,
    action_id: str | None = None,
    is_input: bool,
    expect_list: bool,
    check_runtime: bool = False,
    **_kwargs,
) -> core.StepHandlerProtocol | None:
    if check_runtime:
        mapping_context = RuntimeMappingContext(
            type_id=type_id,
            action_id=action_id,
            is_input=is_input,
            expect_list=expect_list,
        )
        return functools.partial(mapper_step_runtime, mapping_context=mapping_context)

    mapping_function = registry.mapper_registry.get(
        type_id=type_id, action_id=action_id
    )

    if mapping_function is None:
        return None

    mapping_step = mapping_functions[(is_input, expect_list)]

    assert mapping_step is not None, "Incomplete mapping definition"

    return functools.partial(mapping_step, mapping_function=mapping_function)


def default_mapping_steps(
    *,
    type_id: str | None = None,
    action_id_input: str | None = "input",
    action_id_output: str | None = "output",
    mapping_input_expect_list: bool = False,
    mapping_output_expect_list: bool = False,
    mapping_check_runtime: bool = False,
) -> core.StepsDefinitionDict:
    if type_id is None:
        return {}

    return {
        "map_input_default": generic_mapper_step(
            type_id=type_id,
            action_id=action_id_input,
            expect_list=mapping_input_expect_list,
            is_input=True,
            check_runtime=mapping_check_runtime,
        ),
        "map_output_default": generic_mapper_step(
            type_id=type_id,
            action_id=action_id_output,
            expect_list=mapping_output_expect_list,
            is_input=False,
            check_runtime=mapping_check_runtime,
        ),
    }
