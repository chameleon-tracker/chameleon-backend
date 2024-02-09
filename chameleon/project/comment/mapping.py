from chameleon.history import mapping as history
from chameleon.project.comment.models import ChameleonComment
from chameleon.step.mapping import datetime
from chameleon.step.mapping import simple as mapping

mapping.register_simple_mapping_from_dict(
    type_id="comment",
    action_id="create",
    target_object_type=ChameleonComment,
    fields=("description", "description_markup"),
)

mapping.register_simple_mapping_from_object(
    type_id="comment",
    action_id="get",
    target_object_type=dict,
    fields=("id", "description", "description_markup", "creation_time", "ticket_id"),
    custom_converters={"creation_time": datetime.as_utc},
)

mapping.register_simple_mapping_from_object(
    type_id="comment",
    action_id="list",
    target_object_type=dict,
    fields=("id", "description", "description_markup", "creation_time", "ticket_id"),
)

mapping.register_simple_mapping_from_dict(
    type_id="comment",
    action_id="update",
    target_object_type=dict,
    fields=("title",),
)

history.register_mapping_history_output(type_id="comment", action_id="history")
