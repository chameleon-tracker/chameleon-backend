import dataclasses


def create_field(
    *, doc: str | None = None, default=None, **kwargs
) -> dataclasses.Field:
    kwargs["default"] = default  # change default value for 'default' to None

    if doc:
        kwargs["metadata"] = {"doc": doc}

    return dataclasses.field(**kwargs)  # pylint: disable=E3701
