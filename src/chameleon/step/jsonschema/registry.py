import functools

from chameleon.step.registry import registry as reg
from chameleon.step.jsonschema import loader

__all__ = ("validators_registry",)

validators_registry = reg.ProcessorRegistry("validator")


def register_jsonschema_validation(
    *,
    ref: str,
    type_id: str,
    action_id: str | None = None,
):
    key = (type_id, action_id)
    loader.create_validator(ref=ref, type_id=type_id, action_id=action_id)

    validators_registry.register(
        type_id=type_id,
        action_id=action_id,
        processor=functools.partial(loader.json_validation_processor, key=key),
    )
