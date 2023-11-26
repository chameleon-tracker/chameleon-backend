from django.urls import re_path

# initialize mapping
from chameleon.project.project import api
from chameleon.project.project import mapping  # noqa
from chameleon.step.framework import django

processor_create = django.django_json_steps(
    type_id="project",
    action_id_input="create",
    action_id_output="get",
    business=api.project_create_fun,
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
)

urlpatterns = (
    re_path(
        "^$",
        django.method_dispatcher(get=processor_list, post=processor_create),
    ),
    re_path(
        "^/(?P<project_id>[a-zA-Z0-9_-]+)$",
        django.method_dispatcher(get=processor_get, post=processor_update),
    ),
)
