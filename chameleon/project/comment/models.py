from django.db import models

from chameleon.common.django.fields import markup_field
from chameleon.common.django.query import DjangoModelQuery
from chameleon.history.models import ChameleonHistoryBase
from chameleon.history.models import ChameleonObjectWithHistoryBase
from chameleon.project.ticket import models as ticket

__all__ = ["ChameleonComment", "ChameleonCommentHistory"]


class ChameleonCommentHistory(ChameleonHistoryBase):
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)


class ChameleonComment(ChameleonObjectWithHistoryBase):
    class Meta:
        ordering = ["creation_time"]

    history_class = ChameleonCommentHistory
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)

    description = models.TextField(null=True, help_text="Comment description")
    description_markup = markup_field("Comment description")

    # ---- creation only -----
    creation_time = models.DateTimeField(help_text="When comment has been created")
    ticket = models.ForeignKey(ticket.ChameleonTicket, on_delete=models.CASCADE)
