from django.conf import settings

from chameleon.common.django import ChameleonAppConfig
from chameleon.step.validation import jsonschema


class SchemasAppConfig(ChameleonAppConfig):
    def ready(self):
        jsonschema.load_schemas(settings.SCHEMAS_PATHS_OR_MODULES)
