from chameleon.step.mapping import datetime
from chameleon.step.mapping import simple as mapping


def register_mapping_history_output(*, type_id: str, action_id: str | None):
    mapping.register_simple_mapping_from_object(
        type_id=type_id,
        action_id=action_id,
        target_object_type=dict,
        fields=("timestamp", "action", "field", "value_from", "value_to"),
        custom_converters={"timestamp": datetime.as_utc},
    )
