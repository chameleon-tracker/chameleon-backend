from chameleon.step.mapping import registry as mapping_registry
from chameleon.step.validation import registry as validation_registry
from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules("mapping", register_to=mapping_registry)
    autodiscover_modules("validation", register_to=validation_registry)
