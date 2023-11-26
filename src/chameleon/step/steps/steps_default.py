import json
import logging
import typing

from chameleon.step import core
from chameleon.step.steps.steps_json import default_deserialize_json
from chameleon.step.steps.steps_json import default_serialize_json
from chameleon.step.steps.mapping import default_mapping_steps
from chameleon.step.steps.validation import default_validation_steps

logger = logging.getLogger(__name__)

__all__ = ("default_json_steps", "DefaultJsonSteps")

JsonParserProtocol = typing.Callable[[bytes], typing.Any]


class DefaultJsonSteps(typing.TypedDict, total=False):
    json_loads: JsonParserProtocol
    json_dumps: JsonParserProtocol
    type_id: str
    action_id_input: str
    action_id_output: str
    mapping_input_expect_list: bool
    mapping_output_expect_list: bool


def default_json_steps(
    *,
    json_loads: JsonParserProtocol = json.loads,
    json_dumps: JsonParserProtocol = json.dumps,
    type_id: str | None = None,
    action_id_input: str | None = "input",
    action_id_output: str | None = "output",
    mapping_input_expect_list: bool = False,
    mapping_output_expect_list: bool = False,
    mapping_check_runtime: bool = False,
    **kwargs: typing.Unpack[core.StepsDefinitionDict],
) -> core.StepsDefinitionDict:
    """
    Sets default steps for JSON processing.
    This does framework-independent parts

    1. Set serializer and deserializer based on
     `json_loads` and `json_dumps` functions
    2. Creates generic mappers and a validator based on
      mappers and a validator registered for given type and action ids.

    Args:
        json_loads:
        json_dumps:
        type_id:
        action_id_input:
        action_id_output:
        mapping_input_expect_list:
        mapping_output_expect_list:
        mapping_check_runtime:
        **kwargs: rest of the parameters

    Returns:

    """
    json_data: core.StepsDefinitionDict = {
        "deserialize_default": default_deserialize_json(loads=json_loads),
        "serialize_default": default_serialize_json(dumps=json_dumps),
    }

    mapping = default_mapping_steps(
        type_id=type_id,
        action_id_input=action_id_input,
        action_id_output=action_id_output,
        mapping_input_expect_list=mapping_input_expect_list,
        mapping_output_expect_list=mapping_output_expect_list,
        mapping_check_runtime=mapping_check_runtime,
    )

    validation = default_validation_steps(
        type_id=type_id,
        action_id_input=action_id_input,
    )

    result: core.StepsDefinitionDict = {}
    result.update(json_data)
    result.update(mapping)
    result.update(validation)
    result.update(kwargs)
    return result
