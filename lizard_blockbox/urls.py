# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from django.views.generic.simple import direct_to_template

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxView


urlpatterns = patterns(
    '',
    url(r'^$',
        BlockboxView.as_view(),
        name='lizard_blockbox.home'),
    url(r'^table/$',
        BlockboxView.as_view(
            template_name='lizard_blockbox/blockbox-table.html'),
        name='lizard_blockbox_table'),
    url(r'^toggle_measure/',
        'lizard_blockbox.views.toggle_measure',
        name='lizard_blockbox_toggle_measure'),
    url(r'^api/reference/',
        'lizard_blockbox.views.reference_json',
        name="reference_json"),
    url(r'^api/measures/calculated/',
        'lizard_blockbox.views.calculated_measures_json',
        name="calculated_measures_json"),
    url(r'^api/measures/list2/',
        'lizard_blockbox.views.list_measures_json',
        name="measure_list_json"),
    url(r'^api/rivers/maas/',
        'lizard_blockbox.views.maas_river_json',
        name="maas_river_json"),
    url(r'^lb.html/',
        direct_to_template, {'template': 'lizard_blockbox/lb.html'}),
    )
urlpatterns += debugmode_urlpatterns()
