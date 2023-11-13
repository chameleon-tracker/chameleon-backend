from django.db import models

from chameleon.common.fields import markup_field
from chameleon.common.models import ChameleonBaseModel


__all__ = ["ChameleonProject"]


class ChameleonProject(ChameleonBaseModel):
    title = models.CharField(max_length=200, help_text="Project title")
    # Project description
    description = models.TextField(blank=True, help_text="Project description")
    # Project description markup language
    description_markup = markup_field("Project description")
