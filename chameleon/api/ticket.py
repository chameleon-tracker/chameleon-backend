import logging

from django.urls import re_path
from referencing.exceptions import Unresolvable

from chameleon.project.ticket import api
from chameleon.step import core
from chameleon.step.framework import steps_django as django
from chameleon.step.steps.validation import ValidationError

logger = logging.getLogger(__name__)


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


# path variables: `ticket_id` - ticket public ID
processor_get = django.django_json_steps(
    business=api.ticket_get_fun,
    type_id="ticket",
    map_input=None,
    action_id_output="get",
)

processor_update = django.django_json_steps(
    type_id="ticket",
    action_id_input="update",
    action_id_output="get",
    business=api.ticket_update_fun,
    exception_handler={"validate_input": chameleon_validation_error_handler},
)

processor_history = django.django_json_steps(
    type_id="ticket",
    map_input=None,
    action_id_output="history",
    mapping_output_expect_list=True,
    business=api.ticket_history,
)

error_status_to_http = {1: 400}
urlpatterns = (
    re_path(
        "^/(?P<ticket_id>[a-zA-Z0-9_-]+)$",
        django.method_dispatcher(
            get=processor_get,
            post=processor_update,
            error_status_to_http=error_status_to_http,
        ),
    ),
    re_path(
        "^/(?P<ticket_id>[a-zA-Z0-9_-]+)/history$",
        django.method_dispatcher(
            get=processor_history,
            error_status_to_http=error_status_to_http,
        ),
    ),
)