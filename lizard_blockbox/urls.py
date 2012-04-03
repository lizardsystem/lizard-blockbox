# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxView


urlpatterns = patterns(
    '',
    url(r'^$',
        BlockboxView.as_view(),
        {},
        name='lizard_blockbox.home'),
    )
urlpatterns += debugmode_urlpatterns()
