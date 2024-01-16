import logging

from referencing.exceptions import Unresolvable

from chameleon.step import core
from chameleon.step.framework import steps_django as django
from chameleon.step.steps.validation import ValidationError

logger = logging.getLogger(__name__)

__all__ = ["chameleon_json_steps", "method_dispatcher"]

error_status_to_http = {1: 400}


# TODO: create a Chameleon-wide default step and settings
async def chameleon_validation_error_handler(context: core.StepContext):
    if not isinstance(context.exception, (ValidationError, ValueError, Unresolvable)):
        return False

    # TODO: Good start, add and document more errors
    context.error_status = 1  # validation error
    logger.exception("Validation Error", exc_info=context.exception)
    # TODO: pass ValidationError's to the response
    context.output_raw = {
        "error": 10,
    }

    return True


def chameleon_json_steps(**kwargs):
    return django.django_json_steps(
        exception_handler={"validate_input": chameleon_validation_error_handler},
        **kwargs,
    )


def method_dispatcher(**kwargs):
    return django.method_dispatcher(
        error_status_to_http=error_status_to_http,
        **kwargs,
    )
