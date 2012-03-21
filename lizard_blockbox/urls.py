# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxHome


urlpatterns = patterns(
    '',
    url(r'^$',
        BlockboxHome.as_view(),
        {},
        name='lizard_blockbox.homepage'),
    )
urlpatterns += debugmode_urlpatterns()
