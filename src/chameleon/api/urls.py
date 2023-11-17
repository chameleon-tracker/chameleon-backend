from django.urls import include, re_path

from chameleon.api import project

urlpatterns = (re_path("^project", include(project)),)
