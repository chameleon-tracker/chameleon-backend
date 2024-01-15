import logging

from django.urls import re_path

from chameleon.api.chameleon import chameleon_validation_error_handler
from chameleon.project.project import api
from chameleon.project.ticket import api as ticket_api
from chameleon.step.framework import steps_django as django

logger = logging.getLogger(__name__)

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

processor_history = django.django_json_steps(
    type_id="project",
    map_input=None,
    action_id_output="history",
    mapping_output_expect_list=True,
    business=api.project_history,
)

processor_ticket_create = django.django_json_steps(
    type_id="ticket",
    action_id_input="create",
    action_id_output="get",
    business=ticket_api.ticket_create_fun,
    exception_handler={"validate_input": chameleon_validation_error_handler},
)

processor_ticket_list = django.django_json_steps(
    type_id="ticket",
    map_input=None,
    action_id_output="get",
    mapping_output_expect_list=True,
    business=ticket_api.ticket_list_fun,
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
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)/history$",
        django.method_dispatcher(
            get=processor_history,
            error_status_to_http=error_status_to_http,
        ),
    ),
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)/ticket$",
        django.method_dispatcher(
            get=processor_ticket_list,
            post=processor_ticket_create,
            error_status_to_http=error_status_to_http,
        ),
    ),
)
