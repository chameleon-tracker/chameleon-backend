import typing
from django.apps import AppConfig

__all__ = ["AutonameAppConfig"]


@typing.runtime_checkable
class LabelProtocol(typing.Protocol):
    def __call__(self, name: str) -> str | None:
        ...


class AutonameAppConfig(AppConfig):
    """Chameleon project basic application config.

    This class initializes fields `name`, `label` and `default` to make them
    compatible with AppConfig and automatic registration.

    NOTE: `name`, `label` and `default` class-level values will be overriten

    Basic usage:

    >>> class MyAppConfig(AutonameAppConfig):
    ...     ...  # no need to define those parameters by default

    In case of a requirement to override these parameters use as below:

    >>> class MyAppConfig(AutonameAppConfig, default=False):
    ...     ...  # no need to define those parameters by default

    """

    def __init_subclass__(
        cls,
        /,
        name: str | None = None,
        label: str | LabelProtocol | None = None,
        default: bool = True,
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)

        if not name:
            name = cls.__module__

            if "." in name:
                name = name[: name.rfind(".")]  # remove .apps (Django style naming)

        label_value: str | None
        if label is None:
            label_value = None
        else:
            if isinstance(label, str):
                label_value = label
            elif isinstance(label, LabelProtocol):
                label_value = label(name)
            else:
                raise TypeError(
                    f"label must be None, str or LabelProtocol, got {label!r}"
                )

        setattr(cls, "name", name)
        setattr(cls, "default", default)
        if label_value is not None:
            setattr(cls, "label", label_value)


# cleanup namespace
del AppConfig
