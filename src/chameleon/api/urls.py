from django import urls

from chameleon.api import project

urlpatterns = (urls.re_path("project", urls.include(project)),)
