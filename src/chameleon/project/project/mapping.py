from chameleon.project.project.models import ChameleonProject
from chameleon.step.impl import registry

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
