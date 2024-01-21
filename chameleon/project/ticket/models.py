from django.db import models

from chameleon.common.django.query import DjangoModelQuery
from chameleon.history.models import ChameleonHistoryBase
from chameleon.history.models import ChameleonObjectWithHistoryBase
from chameleon.project.project import models as project

__all__ = ["ChameleonTicket", "ChameleonTicketHistory"]


class ChameleonTicketHistory(ChameleonHistoryBase):
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)


class ChameleonTicket(ChameleonObjectWithHistoryBase):
    class Meta:
        ordering = ["creation_time"]

    history_class = ChameleonTicketHistory
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)

    title = models.CharField(max_length=200, help_text="Ticket title")

    # ---- creation only -----
    creation_time = models.DateTimeField(help_text="When ticket has been created")
    project = models.ForeignKey(project.ChameleonProject, on_delete=models.CASCADE)
