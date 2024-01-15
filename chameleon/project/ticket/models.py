from django.db import models

from chameleon.common.django.models import ChameleonBaseModel
from chameleon.common.django.query import DjangoModelQuery
from chameleon.history.models import ChameleonHistoryBase
from chameleon.project.project import models as project

__all__ = ["ChameleonTicket", "ChameleonTicketHistory"]


class ChameleonTicket(ChameleonBaseModel):
    class Meta:
        ordering = ["creation_time"]

    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)

    title = models.CharField(max_length=200, help_text="Ticket title")

    # ---- creation only -----
    creation_time = models.DateTimeField(help_text="When ticket has been created")
    project = models.ForeignKey(project.ChameleonProject, on_delete=models.CASCADE)


class ChameleonTicketHistory(ChameleonHistoryBase):
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)
