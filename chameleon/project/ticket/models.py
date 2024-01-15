from django.db import models

from chameleon.common.models import ChameleonBaseModel
from chameleon.history.models import ChameleonHistoryBase
from chameleon.project.project import models as project

__all__ = ["ChameleonTicket", "ChameleonTicketHistory"]


class ChameleonTicket(ChameleonBaseModel):
    title = models.CharField(max_length=200, help_text="Ticket title")

    # ---- creation only -----
    creation_time = models.DateTimeField(help_text="When issue has been created")
    project = models.ForeignKey(project.ChameleonProject, on_delete=models.CASCADE)


class ChameleonTicketHistory(ChameleonHistoryBase):
    ...
