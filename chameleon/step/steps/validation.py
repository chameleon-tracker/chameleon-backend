import typing

from chameleon.step import core
from chameleon.step import validation

__all__ = ("default_validation_steps", "ValidationError")


def noop_validator(value: typing.Any): ...


class ValidationError(ValueError): ...


def generic_validation_step(
    *, type_id, action_id=None, **_kwargs
) -> core.StepHandlerProtocol:
    async def validation_step(context: core.StepContext):
        value = context.input_raw
        validator_function: core.ProcessorProtocol
        validator_function = validation.registry.get(type_id, action_id, noop_validator)
        result = validator_function(value)
        if result:
            raise ValidationError(result)

    return validation_step


def default_validation_steps(
    *,
    type_id: str | None = None,
    action_id_input: str | None = "input",
    has_validation_input: bool = False,
) -> core.StepsDefinitionDict:
    if type_id is None or has_validation_input:
        return {}

    return {
        "validate_input_default": generic_validation_step(
            type_id=type_id,
            action_id=action_id_input,
        )
    }
