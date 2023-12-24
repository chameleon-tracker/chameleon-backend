# Define automatic mapping
# Create & update & remove object mapping
import datetime
import typing
from collections import abc

from icecream import ic
from chameleon.common.models import ChameleonBaseModel
from chameleon.history.models import ChameleonHistoryBase
from chameleon.step.mapping.simple import register_simple_mapping_from_object


def register_mapping_history_output(*, type_id: str, action_id: str | None):
    register_simple_mapping_from_object(
        type_id=type_id,
        action_id=action_id,
        target_object_type=dict,
        fields=("timestamp", "action", "field", "value_from", "value_to"),
        custom_converters={"timestamp": lambda value: value.isoformat()},
    )


def generate_history_objects[T: ChameleonBaseModel, F: ChameleonHistoryBase](
    *,
    source_object: abc.Mapping[str, typing.Any] | T | None,
    target_object: abc.Mapping[str, typing.Any] | T | None,
    history_model: type[F],
    action: str,
    timestamp: datetime.datetime,
    pk_field: str = "id",
) -> abc.Sequence[F]:
    if source_object is None and target_object is None:
        raise ValueError("source and target objects are both None")

    source_value = object_values(source_object)
    target_value = object_values(target_object)

    source_id = source_value.get(pk_field)
    target_id = target_value.get(pk_field)

    if source_id is None and target_id is None:
        raise ValueError("source and target objects primary keys has not been set")

    if source_id is not None and target_id is not None and source_id != target_id:
        raise ValueError("source and target objects has different primary keys")

    if target_id is None:  # Delete
        return [
            history_model(
                object_id=source_id,
                timestamp=timestamp,
                action=action,
                field=None,
                value_from=None,
                value_to=None,
            )
        ]

    result = []

    if source_id is None:  # Create
        result.append(
            history_model(
                object_id=target_id,
                timestamp=timestamp,
                action=action,
                field=None,
                value_from=None,
                value_to=None,
            )
        )

    difference = object_difference(source_value, target_value)
    ic(timestamp, difference)

    for key, value in difference.items():
        result.append(
            history_model(
                object_id=target_id,
                timestamp=timestamp,
                action=action,
                field=key,
                value_from=value[0],
                value_to=value[1],
            )
        )
    return result


def object_values[T: ChameleonBaseModel](
    source: abc.Mapping[str, typing.Any] | T,
) -> abc.Mapping[str, typing.Any] | None:
    if source is None:
        return {}
    if isinstance(source, ChameleonBaseModel):
        return source.to_dict()
    return source


def object_difference(
    source: abc.Mapping[str, typing.Any],
    target: abc.Mapping[str, typing.Any],
) -> abc.Mapping[str, tuple[typing.Any, typing.Any]]:
    source_keys = frozenset(source.keys())
    target_keys = frozenset(target.keys())

    only_source_keys_keys = source_keys - target_keys
    only_target_target_keys = target_keys - source_keys
    common_keys = source_keys - only_source_keys_keys

    ic(
        source_keys,
        target_keys,
        only_source_keys_keys,
        only_target_target_keys,
        common_keys,
    )

    only_source = {key: (source[key], None) for key in only_source_keys_keys}
    only_target = {key: (None, target[key]) for key in only_target_target_keys}
    common = {
        key: (source[key], target[key])
        for key in common_keys
        if source[key] != target[key]
    }

    result: abc.Mapping[str, tuple[typing.Any, typing.Any]]
    result = dict(**only_source, **only_target, **common)

    return {key: result[key] for key in sorted(result.keys())}
