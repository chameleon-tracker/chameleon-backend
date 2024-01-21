import logging

from django.urls import re_path

from chameleon.api import chameleon
from chameleon.project.comment import api

logger = logging.getLogger(__name__)

# path variables: `comment_id` - comment public ID
processor_get = chameleon.chameleon_json_steps(
    business=api.comment_get_fun,
    type_id="comment",
    map_input=None,
    action_id_output="get",
)

processor_update = chameleon.chameleon_json_steps(
    type_id="comment",
    action_id_input="update",
    action_id_output="get",
    business=api.comment_update_fun,
)

processor_history = chameleon.chameleon_json_steps(
    type_id="comment",
    map_input=None,
    action_id_output="history",
    mapping_output_expect_list=True,
    business=api.comment_history,
)

urlpatterns = (
    re_path(
        "^/(?P<comment_id>[a-zA-Z0-9_-]+)$",
        chameleon.method_dispatcher(get=processor_get, post=processor_update),
    ),
    re_path(
        "^/(?P<comment_id>[a-zA-Z0-9_-]+)/history$",
        chameleon.method_dispatcher(get=processor_history),
    ),
)
