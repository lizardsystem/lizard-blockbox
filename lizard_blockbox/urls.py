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
    url(r'^api/reference/',
        'lizard_blockbox.views.reference_json',
        name="reference_json"),
    )
urlpatterns += debugmode_urlpatterns()
