from chameleon.history import mapping as history
from chameleon.project.project.models import ChameleonProject
from chameleon.step.mapping import datetime
from chameleon.step.mapping import simple as mapping

mapping.register_simple_mapping_from_dict(
    type_id="project",
    action_id="create",
    target_object_type=ChameleonProject,
    fields=("name", "summary", "description", "description_markup"),
)

mapping.register_simple_mapping_from_object(
    type_id="project",
    action_id="get",
    target_object_type=dict,
    fields=(
        "id",
        "name",
        "summary",
        "creation_time",
        "description",
        "description_markup",
    ),
    custom_converters={"creation_time": datetime.as_utc, "id": str},
)

mapping.register_simple_mapping_from_object(
    type_id="project",
    action_id="list",
    target_object_type=dict,
    fields=("id", "name", "summary", "creation_time"),
    custom_converters={"creation_time": datetime.as_utc, "id": str},
)

mapping.register_simple_mapping_from_dict(
    type_id="project",
    action_id="update",
    target_object_type=dict,
    fields=("name", "summary", "description", "description_markup"),
)

history.register_mapping_history_output(type_id="project", action_id="history")
