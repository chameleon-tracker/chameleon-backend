from django.contrib import admin
from . import models


@admin.register(models.ChameleonProject)
class ChameleonProjectAdmin(admin.ModelAdmin):
    pass
