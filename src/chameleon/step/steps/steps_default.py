import json
import logging
import typing

from chameleon.step import core
from chameleon.step.steps.mapping import default_mapping_steps
from chameleon.step.steps.validation import default_validation_steps
from chameleon.step.steps.steps_json import deserialize_json
from chameleon.step.steps.steps_json import serialize_json

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
        json_loads: Funtion to parses JSON from the request. *MUST* be secure
        json_dumps: Funtion to dumps JSON from the request. *MUST* be secure
        type_id: Type id used for mapping and validation.
        action_id_input: Action id used for input mapping and input validation.
        action_id_output: Action id used for output mapping and output validation.
        mapping_input_expect_list: If input mapping expects list of objects.
        mapping_output_expect_list: If output mapping expects list of objects.
        mapping_check_runtime: Mapping should resolve mapper functions in runtime.
        **kwargs: rest of the parameters
    """

    json_steps: core.StepsDefinitionDict = {
        "deserialize_default": deserialize_json(loads=json_loads),
        "serialize_default": serialize_json(dumps=json_dumps),
    }

    mapping_steps = default_mapping_steps(
        type_id=type_id,
        action_id_input=action_id_input,
        action_id_output=action_id_output,
        mapping_input_expect_list=mapping_input_expect_list,
        mapping_output_expect_list=mapping_output_expect_list,
        mapping_check_runtime=mapping_check_runtime,
    )

    validation_steps = default_validation_steps(
        type_id=type_id,
        action_id_input=action_id_input,
    )

    result_steps: core.StepsDefinitionDict = {}
    result_steps.update(json_steps)
    result_steps.update(mapping_steps)
    result_steps.update(validation_steps)
    result_steps.update(kwargs)
    return result_steps
