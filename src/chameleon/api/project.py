from django.urls import re_path

from chameleon.step import core

from chameleon.step.impl import django
from chameleon.step.impl import registry

from chameleon.project.project.models import ChameleonProject


registry.register_simple_mapping_dict(
    type_id="project",
    action_id="create",
    target_object_type=ChameleonProject,
    fields=("title", "description", "description_markup"),
)

registry.register_simple_mapping_object(
    type_id="project",
    action_id="get",
    target_object_type=dict,
    fields=("id", "title", "description", "description_markup"),
)

registry.register_simple_mapping_object(
    type_id="project",
    action_id="list",
    target_object_type=dict,
    fields=("id", "title"),
)

registry.register_simple_mapping_dict(
    type_id="project",
    action_id="update",
    target_object_type=dict,
    fields=("title", "description", "description_markup"),
)


async def project_create_fun(context: core.StepContext):
    project = context.input_business
    print(f"{project=!r}")
    await project.asave(force_insert=True)
    context.output_business = project


async def project_list_fun(context: core.StepContext):
    context.output_business = [
        project async for project in ChameleonProject.objects.all()
    ]


async def project_get_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    context.output_business = await ChameleonProject.objects.aget(pk=project_id)


async def project_update_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    project_data = context.input_business
    project = await ChameleonProject.objects.aget(pk=project_id)
    print(f"==>> {project=!r}")
    await project.update(commit=True, **project_data)
    context.output_business = project


processor_create = django.django_default_json_hooks(
    type_id="project",
    action_id_input="create",
    action_id_output="get",
    business=project_create_fun,
)

processor_list = django.django_default_json_hooks(
    type_id="project",
    map_input=None,
    action_id_output="get",
    mapping_output_expect_list=True,
    business=project_list_fun,
)

# path variables: `project_id` - project public ID
processor_get = django.django_default_json_hooks(
    business=project_get_fun,
    type_id="project",
    map_input=None,
    action_id_output="get",
)

processor_update = django.django_default_json_hooks(
    type_id="project",
    action_id_input="update",
    action_id_output="get",
    business=project_update_fun,
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
