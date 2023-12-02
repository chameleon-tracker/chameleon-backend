from django.apps import AppConfig

from chameleon.common import ChameleonAppConfig


class ProjectConfig(ChameleonAppConfig, AppConfig):
    ...
