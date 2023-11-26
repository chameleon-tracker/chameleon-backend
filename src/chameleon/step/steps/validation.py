from chameleon.step import core
from chameleon.step.registry import validators_registry

__all__ = ("default_validation_steps",)


def generic_validation_step(
    *, type_id, action_id=None, **_kwargs
) -> core.StepHandlerProtocol:
    async def validation_step(context: core.StepContext):
        value = context.input_raw
        validator_function = validators_registry.get(type_id, action_id)
        if validator_function is not None:
            validator_function(value)

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
