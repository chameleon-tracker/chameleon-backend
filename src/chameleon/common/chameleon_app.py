from django.apps import AppConfig

__all__ = ["ChameleonAppConfig"]


class ChameleonAppConfig(AppConfig):
    """Chameleon project basic application config.

    This class initializes fields `name`, `label` and `default` to make them
    compatible with AppConfig and automatic registration.

    NOTE: name, label and default class-level values will be overriten

    Basic usage:

    >>> class MyAppConfig(ChameleonAppConfig):
    ...     ...  # no need to define those parameters by default

    In case of a requirement to override these parameters use as below:

    >>> class MyAppConfig(ChameleonAppConfig, default=False):
    ...     ...  # no need to define those parameters by default

    """

    def __init_subclass__(cls, /, name=None, label=None, default=True, **kwargs):
        super().__init_subclass__(**kwargs)

        if not name:
            name = cls.__module__

            if "." in name:
                name = name[: name.rfind(".")]

        if not label:
            label = name.replace(".", "_")

        setattr(cls, "name", name)
        setattr(cls, "label", label)
        setattr(cls, "default", default)


# cleanup namespace
del AppConfig
