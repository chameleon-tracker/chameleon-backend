import typing
from collections import abc
from chameleon.step.mapping import registry


__all__ = (
    "register_simple_mapping",
    "register_simple_mapping_from_dict",
    "register_simple_mapping_from_object",
    "get_field_attr",
    "get_field_dict",
    "get_field_depth",
    "FieldConverterProtocol",
)

GetattrProtocol = abc.Callable[[typing.Any, str], typing.Any]
FieldConverterProtocol = abc.Callable[[typing.Any], typing.Any]


def register_simple_mapping(
    *,
    type_id: str,
    action_id: str | None = None,
    target_object_type: typing.Any,
    get_field_fun: GetattrProtocol,
    include_none=False,
    fields: abc.Sequence[str] | None = None,
    custom_mapping: abc.Mapping[str, str] | None = None,
    custom_converters: abc.Mapping[str, FieldConverterProtocol] | None = None,
):
    """Register simple mapping function.

    type_id & action_id define target processor name
    target_object_type is object_type
    """

    if fields:
        plain_mapping = {field: field for field in fields}
    else:
        plain_mapping = {}

    if custom_mapping:
        field_mapping = {**custom_mapping, **plain_mapping}
    else:
        field_mapping = plain_mapping

    if not field_mapping:
        raise ValueError("No field mapping defined")

    if not custom_converters:
        custom_converters = {}

    unknown_converters = set(custom_converters.keys()) - field_mapping.keys()

    if unknown_converters:
        raise ValueError(f"Unknown field converters provided: {unknown_converters}")

    def mapping(source):
        kwargs = {}
        for target_field, source_field in field_mapping.items():
            converter = custom_converters.get(target_field)
            if converter is None:
                target_field_value = get_field_fun(source, source_field)
            else:
                target_field_value = converter(get_field_fun(source, source_field))

            if target_field_value is not None or include_none:
                kwargs[target_field] = target_field_value

        return target_object_type(**kwargs)

    registry.register(type_id=type_id, action_id=action_id, processor=mapping)


def register_simple_mapping_from_dict(
    *,
    type_id: str,
    action_id: str | None = None,
    target_object_type,
    include_none=False,
    fields: abc.Sequence[str] | None = None,
    custom_mapping: abc.Mapping[str, str] | None = None,
    custom_converters: abc.Mapping[str, FieldConverterProtocol] | None = None,
):
    register_simple_mapping(
        type_id=type_id,
        action_id=action_id,
        target_object_type=target_object_type,
        include_none=include_none,
        get_field_fun=get_field_depth(get_field_dict),
        fields=fields,
        custom_mapping=custom_mapping,
        custom_converters=custom_converters,
    )


def register_simple_mapping_from_object(
    *,
    type_id: str,
    action_id: str | None = None,
    target_object_type,
    include_none=False,
    fields: abc.Sequence[str] | None = None,
    custom_mapping: abc.Mapping[str, str] | None = None,
    custom_converters: abc.Mapping[str, FieldConverterProtocol] | None = None,
):
    register_simple_mapping(
        type_id=type_id,
        action_id=action_id,
        target_object_type=target_object_type,
        include_none=include_none,
        get_field_fun=get_field_depth(get_field_attr),
        fields=fields,
        custom_mapping=custom_mapping,
        custom_converters=custom_converters,
    )


def get_field_attr(source, field: str):
    return getattr(source, field)


def get_field_dict(source, field: str):
    return source.get(field)


def get_field_depth(get_field_fun) -> GetattrProtocol:
    def get_field_depth_fun(source, complex_field):
        fields = complex_field.split(".")
        # check if there's a fields to traverse
        value = source
        for field in fields:
            value = get_field_fun(source, field)

        return value

    return get_field_depth_fun
