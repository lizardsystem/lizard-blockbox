# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxHome
from lizard_blockbox.views import ReachChoiceView


urlpatterns = patterns(
    '',
    url(r'^raai/some_slug/$',
        BlockboxHome.as_view(),
        {},
        name='lizard_blockbox.reach'),
    url(r'^$',
        ReachChoiceView.as_view(),
        name='lizard_blockbox.reach_choice'),
    )
urlpatterns += debugmode_urlpatterns()
