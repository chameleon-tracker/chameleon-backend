import json
import logging
import typing

from chameleon.step.impl import generic_mapping
from chameleon.step.impl import generic_validation
from chameleon.step.impl import deserialize_json
from chameleon.step.impl import serialize_json


logger = logging.getLogger(__name__)

__all__ = ("default_json_steps",)

JsonParserProtocol = typing.Callable[[bytes], typing.Any]


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
    **kwargs,
):
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
    json_data = dict(
        deserialize_default=deserialize_json(loads=json_loads),
        serialize_default=serialize_json(dumps=json_dumps),
    )

    mapping = generic_mapping(
        type_id=type_id,
        action_id_input=action_id_input,
        action_id_output=action_id_output,
        mapping_input_expect_list=mapping_input_expect_list,
        mapping_output_expect_list=mapping_output_expect_list,
        mapping_check_runtime=mapping_check_runtime,
    )

    validation = generic_validation(
        type_id=type_id,
        action_id_input=action_id_input,
    )

    return {**json_data, **mapping, **validation, **kwargs}
