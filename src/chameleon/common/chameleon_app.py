from chameleon.common.app.autoname import AutonameAppConfig

__all__ = ["ChameleonAppConfig"]


def chameleon_label(name: str) -> str | None:
    return name.replace(".", "_")


class ChameleonAppConfig(AutonameAppConfig, default=False, label=chameleon_label):
    ...
