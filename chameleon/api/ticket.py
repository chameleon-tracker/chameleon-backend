import logging

from django.urls import re_path

from chameleon.api import chameleon
from chameleon.project.ticket import api

logger = logging.getLogger(__name__)

# path variables: `ticket_id` - ticket public ID
processor_get = chameleon.chameleon_json_steps(
    business=api.ticket_get_fun,
    type_id="ticket",
    map_input=None,
    action_id_output="get",
)

processor_update = chameleon.chameleon_json_steps(
    type_id="ticket",
    action_id_input="update",
    action_id_output="get",
    business=api.ticket_update_fun,
)

processor_history = chameleon.chameleon_json_steps(
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
        chameleon.method_dispatcher(get=processor_get, post=processor_update),
    ),
    re_path(
        "^/(?P<ticket_id>[a-zA-Z0-9_-]+)/history$",
        chameleon.method_dispatcher(get=processor_history),
    ),
)
