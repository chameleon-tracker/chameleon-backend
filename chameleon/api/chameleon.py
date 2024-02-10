import enum
import logging

import orjson
from django.core.exceptions import ObjectDoesNotExist
from referencing.exceptions import Unresolvable

from chameleon.step import core
from chameleon.step.framework import steps_django as django
from chameleon.step.steps.validation import ValidationError

logger = logging.getLogger(__name__)

__all__ = ["chameleon_json_steps", "method_dispatcher"]


class ChameleonErrors(enum.IntEnum):
    JSON_DESERIALIZE_ERROR = 1
    JSON_SERIALIZE_ERROR = 2
    JSON_VALIDATION_FAILED = 3
    OBJECT_NOT_FOUND = 10
    INTERNAL_ERROR = 999


error_status_to_http = {
    ChameleonErrors.JSON_DESERIALIZE_ERROR: 400,
    ChameleonErrors.JSON_VALIDATION_FAILED: 400,
    ChameleonErrors.JSON_SERIALIZE_ERROR: 500,
    ChameleonErrors.OBJECT_NOT_FOUND: 404,
    ChameleonErrors.INTERNAL_ERROR: 500,
}


async def chameleon_validation_error_handler(context: core.StepContext):
    if not isinstance(context.exception, (ValidationError, ValueError, Unresolvable)):
        return False

    context.error_status = ChameleonErrors.JSON_VALIDATION_FAILED
    logger.exception("Validation Error", exc_info=context.exception)

    # TODO: map validation error fields to output_raw
    # TODO: define error_output object
    # TODO: have better mechanism to map output
    context.output_raw = {
        "error": ChameleonErrors.JSON_VALIDATION_FAILED,
    }

    return True


async def chameleon_business_error_handler(context: core.StepContext) -> bool:
    if not isinstance(context.exception, ObjectDoesNotExist):
        return False

    context.error_status = ChameleonErrors.OBJECT_NOT_FOUND

    context.output_raw = {
        "error": ChameleonErrors.OBJECT_NOT_FOUND,
    }

    return True


async def chameleon_json_deserialize(context: core.StepContext) -> bool:
    if not isinstance(context.exception, orjson.JSONDecodeError):
        return False

    context.error_status = ChameleonErrors.JSON_DESERIALIZE_ERROR

    context.output_raw = {
        "error": ChameleonErrors.JSON_DESERIALIZE_ERROR,
    }

    return True


def chameleon_json_steps(**kwargs):
    return django.django_json_steps(
        json_loads=orjson.loads,
        json_dumps=orjson.dumps,
        exception_handler_default={
            "validate_input": chameleon_validation_error_handler,
            "business": chameleon_business_error_handler,
            "deserialize": chameleon_json_deserialize,
        },
        **kwargs,
    )


def method_dispatcher(**kwargs):
    return django.method_dispatcher(
        error_status_to_http=error_status_to_http,
        **kwargs,
    )
