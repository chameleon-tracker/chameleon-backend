import typing

from chameleon.step.registry import registry

__all__ = (
    "mapper_registry",
    "register_simple_mapping",
    "register_simple_mapping_dict",
    "register_simple_mapping_object",
    "get_field_attr",
    "get_field_dict",
    "get_field_depth",
)

GetattrProtocol = typing.Callable[[typing.Any, str], typing.Any]

mapper_registry = registry.ProcessorRegistry("mapper")


def register_simple_mapping(
    *,
    type_id: str,
    action_id: str | None = None,
    target_object_type: typing.Any,
    get_field_fun: GetattrProtocol,
    include_none=False,
    fields: typing.Sequence[str] | None = None,
    custom_mapping: typing.Mapping[str, str] | None = None,
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

    def mapping(source):
        kwargs = {}
        for dest_field, source_field in field_mapping.items():
            dest_value = get_field_fun(source, source_field)
            if dest_value is not None or include_none:
                kwargs[dest_field] = dest_value

        return target_object_type(**kwargs)

    mapper_registry.register(type_id=type_id, action_id=action_id, processor=mapping)


def register_simple_mapping_dict(
    *,
    type_id: str,
    action_id: str | None = None,
    target_object_type,
    include_none=False,
    fields: typing.Sequence[str] | None = None,
    custom_mapping: typing.Mapping[str, str] | None = None,
):
    register_simple_mapping(
        type_id=type_id,
        action_id=action_id,
        target_object_type=target_object_type,
        include_none=include_none,
        get_field_fun=get_field_depth(get_field_dict),
        fields=fields,
        custom_mapping=custom_mapping,
    )


def register_simple_mapping_object(
    *,
    type_id: str,
    action_id: str | None = None,
    target_object_type,
    include_none=False,
    fields: typing.Sequence[str] | None = None,
    custom_mapping: typing.Mapping[str, str] | None = None,
):
    register_simple_mapping(
        type_id=type_id,
        action_id=action_id,
        target_object_type=target_object_type,
        include_none=include_none,
        get_field_fun=get_field_depth(get_field_attr),
        fields=fields,
        custom_mapping=custom_mapping,
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
