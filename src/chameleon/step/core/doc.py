import dataclasses


def create_field(*, doc: str = None, default=None, **kwargs) -> dataclasses.Field:
    if not doc:
        return dataclasses.field(default=default, **kwargs)

    return dataclasses.field(default=default, metadata={"doc": doc}, **kwargs)
