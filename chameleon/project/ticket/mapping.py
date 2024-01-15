from chameleon.project.ticket.models import ChameleonTicket
from chameleon.step.mapping import simple as mapping
from chameleon.step.mapping import datetime
from chameleon.history.utils import register_mapping_history_output

mapping.register_simple_mapping_from_dict(
    type_id="ticket",
    action_id="create",
    target_object_type=ChameleonTicket,
    fields=("title",),
)

mapping.register_simple_mapping_from_object(
    type_id="ticket",
    action_id="get",
    target_object_type=dict,
    fields=("id", "title", "creation_time", "project_id"),
    custom_converters={"creation_time": datetime.to_external_value},
)

mapping.register_simple_mapping_from_object(
    type_id="ticket",
    action_id="list",
    target_object_type=dict,
    fields=("id", "title", "creation_time", "project_id"),
)

mapping.register_simple_mapping_from_dict(
    type_id="ticket",
    action_id="update",
    target_object_type=dict,
    fields=("title",),
)

register_mapping_history_output(type_id="ticket", action_id="history")
