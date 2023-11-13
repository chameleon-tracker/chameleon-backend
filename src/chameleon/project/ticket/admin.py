from django.contrib import admin
from . import models


@admin.register(models.ChameleonTicket)
class ChameleonTicketAdmin(admin.ModelAdmin):
    pass
