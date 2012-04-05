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
    url(r'^api/measures/calculated/',
        'lizard_blockbox.views.calculated_measures_json',
        name="calculated_measures_json"),
    url(r'^api/measures/list/',
        'lizard_blockbox.views.list_measures_json',
        name="measure_list_json"),
    url(r'^api/rivers/maas/',
        'lizard_blockbox.views.maas_river_json',
        name="maas_river_json"),
    )
urlpatterns += debugmode_urlpatterns()
