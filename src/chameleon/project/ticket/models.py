from django.db import models

from chameleon.common.models import ChameleonBaseModel
from chameleon.project.project import models as project
from chameleon.common.fields import markup_field

__all__ = ["ChameleonTicket"]


class ChameleonTicket(ChameleonBaseModel):
    title = models.CharField(max_length=200, help_text="Ticket title")

    description = models.TextField(blank=True, help_text="Ticket description")
    description_markup = markup_field("Project issue description")

    # creation only
    project = models.ForeignKey(project.ChameleonProject, on_delete=models.CASCADE)
