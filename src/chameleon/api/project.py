import logging

from django.urls import re_path

# initialize mapping
from chameleon.project.project import api

# TODO: Extend Django App initialization to handle this auto-magically
from chameleon.project.project import mapping  # noqa
from chameleon.project.project import validation  # noqa

from chameleon.step import core
from chameleon.step.framework import django
from chameleon.step.steps.validation import ValidationError

from referencing.exceptions import Unresolvable

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


processor_create = django.django_json_steps(
    type_id="project",
    action_id_input="create",
    action_id_output="get",
    business=api.project_create_fun,
    exception_handler={"validate_input": chameleon_validation_error_handler},
)

processor_list = django.django_json_steps(
    type_id="project",
    map_input=None,
    action_id_output="get",
    mapping_output_expect_list=True,
    business=api.project_list_fun,
)

# path variables: `project_id` - project public ID
processor_get = django.django_json_steps(
    business=api.project_get_fun,
    type_id="project",
    map_input=None,
    action_id_output="get",
)

processor_update = django.django_json_steps(
    type_id="project",
    action_id_input="update",
    action_id_output="get",
    business=api.project_update_fun,
    exception_handler={"validate_input": chameleon_validation_error_handler},
)

error_status_to_http = {1: 400}
urlpatterns = (
    re_path(
        "^$",
        django.method_dispatcher(
            get=processor_list,
            post=processor_create,
            error_status_to_http=error_status_to_http,
        ),
    ),
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)$",
        django.method_dispatcher(
            get=processor_get,
            post=processor_update,
            error_status_to_http=error_status_to_http,
        ),
    ),
)
