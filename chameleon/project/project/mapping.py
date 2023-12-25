from chameleon.project.project.models import ChameleonProject
from chameleon.step.mapping import simple as mapping
from chameleon.history.utils import register_mapping_history_output

mapping.register_simple_mapping_from_dict(
    type_id="project",
    action_id="create",
    target_object_type=ChameleonProject,
    fields=("title", "description", "description_markup"),
)

mapping.register_simple_mapping_from_object(
    type_id="project",
    action_id="get",
    target_object_type=dict,
    fields=("id", "title", "description", "description_markup"),
)

mapping.register_simple_mapping_from_object(
    type_id="project",
    action_id="list",
    target_object_type=dict,
    fields=("id", "title"),
)

mapping.register_simple_mapping_from_dict(
    type_id="project",
    action_id="update",
    target_object_type=dict,
    fields=("title", "description", "description_markup"),
)

register_mapping_history_output(type_id="project", action_id="history")
