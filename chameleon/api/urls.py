from django import urls

from chameleon.api import project
from chameleon.api import ticket

urlpatterns = (
    urls.re_path("project", urls.include(project)),
    urls.re_path("ticket", urls.include(ticket)),
)
