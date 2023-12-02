from chameleon.common import ChameleonAppConfig
from chameleon.step.validation import jsonschema

from django.conf import settings


class AppConfig(ChameleonAppConfig):
    def ready(self):
        jsonschema.load_schemas(settings.SCHEMAS_PATHS)
