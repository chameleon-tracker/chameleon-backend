import functools
import typing

import jsonschema
from referencing.jsonschema import SchemaRegistry

from chameleon.step.impl.registry import registry as reg


__all__ = ("validator_registry",)

validator_registry = reg.ProcessorRegistry("validator")
schema_registry: SchemaRegistry = SchemaRegistry()
validators: typing.MutableMapping[tuple[str, str | None], jsonschema.Validator] = {}
JsonValidator = jsonschema.Draft202012Validator


def update_validators():
    """Update validators after schema_registry evolved."""
    for key, validator in list(validators.items()):
        validators[key] = validator.evolve(registry=schema_registry)


async def validation_processor(value: typing.Any, *, key: tuple[str, str | None]):
    return list(validators[key].iter_errors(value)) or None


def register_jsonschema_validation(
    *,
    ref: str,
    type_id: str,
    action_id: str | None = None,
):
    key = (type_id, action_id)
    if key not in validators:
        validators[key] = JsonValidator(schema={"$ref": ref}, registry=schema_registry)

    validator_registry.register(
        type_id=type_id,
        action_id=action_id,
        processor=functools.partial(validation_processor, key=key),
    )
