from chameleon.step.impl.registry import validator_registry
from chameleon.step import core


__all__ = ("generic_validation",)


def generic_validation_handler(
    *, type_id, action_id=None, **_kwargs
) -> core.StepHandlerProtocol:
    async def validation_handler(context: core.StepContext):
        value = context.input_raw
        validator_function = validator_registry.get(type_id, action_id)
        if validator_function is not None:
            validator_function(value)

    return validation_handler


def generic_validation(
    *,
    type_id: str | None = None,
    action_id_input: str | None = "input",
    has_validation_input: bool = False,
):
    if type_id is None or has_validation_input:
        return {}

    return {
        "validate_input_default": generic_validation_handler(
            type_id=type_id,
            action_id=action_id_input,
        )
    }
