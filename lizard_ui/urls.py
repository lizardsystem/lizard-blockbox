import logging

from django.conf import settings
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.static import static
from staticfiles.urls import staticfiles_urlpatterns


import lizard_ui.views

logger = logging.getLogger(__name__)


def debugmode_urlpatterns():
    # Staticfiles url patterns.
    patterns = staticfiles_urlpatterns()
    # User-uploaded media patterns. Used to be arranged by django-staticfiles.
    prefix = settings.MEDIA_URL
    root = settings.MEDIA_ROOT
    if prefix and root:
        patterns += static(prefix, document_root=root)
    else:
        logger.warn("Can't find MEDIA_URL (%s) and/or MEDIA_ROOT (%s).",
                    prefix, root)
    return patterns


urlpatterns = patterns(
    '',
    url(r'^accounts/login/$',
        lizard_ui.views.LoginView.as_view(),
        name='lizard_ui.login'),
    url(r'^accounts/logout/$',
        lizard_ui.views.LogoutView.as_view(),
        name='lizard_ui.logout'),
)
