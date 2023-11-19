import dataclasses
import typing

import jsonschema
import jsonschema.protocols as json_protocols
import yaml
import referencing
from referencing.jsonschema import SchemaRegistry

from chameleon.step.impl.registry import registry as reg


__all__ = ("SchemaDefinition", "create_all_validators", "validator_registry")

validator_registry = reg.ProcessorRegistry("validator")
global_validators: typing.MutableMapping[str, json_protocols.Validator] = {}


def register_jsonschema_validation(
    *,
    uri: str,
    type_id: str,
    action_id: str | None = None,
):
    async def validation_processor(value: typing.Any):
        global_validators[uri].validate(value)

    validator_registry.register(
        type_id=type_id, action_id=action_id, processor=validation_processor
    )


def load_schema(filename):
    with open(filename) as f:  # pylint: disable=W1514
        data = f.read()
    return yaml.safe_load(data)


class SchemaContentsProtocol(typing.Protocol):
    def get(self, key: str, default: typing.Self | None) -> typing.Self | None:
        ...

    def keys(self) -> typing.Sequence[str]:
        ...


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class SchemaDefinition:
    schema_filename: str
    element_uri_prefix: str
    definition_path: str = "$defs"


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class SchemaDefinitionInternal:
    element_uri_prefix: str
    definition_path: str
    schema_id: str
    schema_data: dict
    schema_version: str


def create_all_validators(
    *definitions: SchemaDefinition,
    validator_type: type[json_protocols.Validator] = jsonschema.Draft202012Validator,
):
    validators = {}
    schema_definitions = []
    schemas_registry = []

    for definition in definitions:
        schema_data = load_schema(definition.schema_filename)
        validator_type.check_schema(schema_data)

        schema_res = referencing.Resource.from_contents(schema_data)
        schema_id = schema_res.id()
        if schema_id is None:
            raise ValueError("Schema $id must be present.")

        schemas_registry.append((schema_id, schema_res))

        schema_definitions.append(
            SchemaDefinitionInternal(
                element_uri_prefix=definition.element_uri_prefix,
                definition_path=definition.definition_path,
                schema_id=schema_id,
                schema_version=schema_data["$schema"],
                schema_data=schema_data,
            )
        )

    registry = SchemaRegistry().with_resources(schemas_registry)

    for schema_definition in schema_definitions:
        validators.update(
            validator_load_multi(
                registry=registry,
                schema=schema_definition,
                validator_type=validator_type,
            )
        )

    return validators


def validator_load_multi(
    *,
    registry: SchemaRegistry,
    schema: SchemaDefinitionInternal,
    validator_type: type[json_protocols.Validator],
):
    """

    Loader function "extracts" a definition from definition path.

    Args:
        registry:
        schema: loaded
        validator_type:

    Returns:
    """
    yield (
        schema.element_uri_prefix,
        validator_type(schema={"$ref": schema.schema_id}, registry=registry),
    )
    names = schema_traverse(schema.schema_data, schema.definition_path).keys()

    for name in names:
        element_id = f"{schema.element_uri_prefix}/{name}"
        element_schema = {
            "$ref": f"{schema.schema_id}#/{schema.definition_path}/{name}"
        }

        validator = validator_type(schema=element_schema, registry=registry)
        yield element_id, validator


def schema_traverse(schema_contents: dict, path: str) -> typing.Any:
    """Traverse slash-separated path in dict-like structure."""
    parts = path.split("/")

    data = schema_contents
    for part in parts:
        data = data.get(part, {})
    return data or None
