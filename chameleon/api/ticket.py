import logging

from django.urls import re_path

from chameleon.api.chameleon import chameleon_validation_error_handler
from chameleon.project.ticket import api
from chameleon.step.framework import steps_django as django

logger = logging.getLogger(__name__)

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
