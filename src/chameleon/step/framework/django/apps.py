from django.apps import AppConfig


class StepsDjangoConfig(AppConfig):
    name = "chameleon.step.framework.django"
    label = "chameleon_step_framework_django"
    default = True

    def ready(self):
        super().ready()
        self.module.autodiscover()
