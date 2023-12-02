import json

from chameleon.step import core

# File named steps_json.py because of blackd integration in my editor.
# Files named json.py or types.py are not welcome there.

HTTP_METHODS_WITH_INPUT = {"POST", "PUT"}


async def check_content_type_json(context: core.StepContext):
    request_method: str = context.request_info.method

    if request_method in HTTP_METHODS_WITH_INPUT:
        if context.request_info.content_type != "application/json":
            raise ValueError("Unsupported content type")


def default_deserialize_json(loads=json.loads):
    async def deserialize_json(context: core.StepContext):
        request_method = context.request_info.method

        if request_method in HTTP_METHODS_WITH_INPUT:
            context.input_raw = loads(context.request_body)

    return deserialize_json


def default_serialize_json(dumps=json.dumps):
    async def serialize_json(context: core.StepContext):
        if context.output_raw is None:
            response_body = b""
        else:
            value = dumps(context.output_raw)
            if isinstance(value, bytes):
                response_body = value
            elif isinstance(value, str):
                response_body = value.encode("utf-8")
            else:
                raise ValueError("Dump function must return bytes or str")

        context.response_body = response_body

    return serialize_json
