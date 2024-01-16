import logging

from django.urls import re_path

from chameleon.api import chameleon
from chameleon.project.project import api
from chameleon.project.ticket import api as ticket_api

logger = logging.getLogger(__name__)

processor_create = chameleon.chameleon_json_steps(
    type_id="project",
    action_id_input="create",
    action_id_output="get",
    business=api.project_create_fun,
)

processor_list = chameleon.chameleon_json_steps(
    type_id="project",
    map_input=None,
    action_id_output="get",
    mapping_output_expect_list=True,
    business=api.project_list_fun,
)

# path variables: `project_id` - project public ID
processor_get = chameleon.chameleon_json_steps(
    business=api.project_get_fun,
    type_id="project",
    map_input=None,
    action_id_output="get",
)

processor_update = chameleon.chameleon_json_steps(
    type_id="project",
    action_id_input="update",
    action_id_output="get",
    business=api.project_update_fun,
)

processor_history = chameleon.chameleon_json_steps(
    type_id="project",
    map_input=None,
    action_id_output="history",
    mapping_output_expect_list=True,
    business=api.project_history,
)

processor_ticket_create = chameleon.chameleon_json_steps(
    type_id="ticket",
    action_id_input="create",
    action_id_output="get",
    business=ticket_api.ticket_create_fun,
)

processor_ticket_list = chameleon.chameleon_json_steps(
    type_id="ticket",
    map_input=None,
    action_id_output="get",
    mapping_output_expect_list=True,
    business=ticket_api.ticket_list_fun,
)

urlpatterns = (
    re_path(
        "^$",
        chameleon.method_dispatcher(get=processor_list, post=processor_create),
    ),
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)$",
        chameleon.method_dispatcher(get=processor_get, post=processor_update),
    ),
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)/history$",
        chameleon.method_dispatcher(get=processor_history),
    ),
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)/ticket$",
        chameleon.method_dispatcher(
            get=processor_ticket_list, post=processor_ticket_create
        ),
    ),
)
