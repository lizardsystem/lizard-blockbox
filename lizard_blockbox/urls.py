# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxView, PlainGraphMapView
from lizard_blockbox.views import SelectedMeasuresView
from lizard_blockbox.views import BookmarkedMeasuresView


urlpatterns = patterns(
    '',
    url(r'^$',
        BlockboxView.as_view(),
        name='lizard_blockbox.home'),
    url(r'^report/$',
        'lizard_blockbox.views.generate_report',
        name='lizard_blockbox.generate_report'),
    url(r'^graphmapview/$',
        PlainGraphMapView.as_view(),
        name='lizard_blockbox.plain_graph_map'),
    url(r'^csv/$',
        'lizard_blockbox.views.generate_csv',
        name='lizard_blockbox.generate_csv'),
    url(r'^geselecteerd/$',
        SelectedMeasuresView.as_view(),
        name='lizard_blockbox.selected_measures'),
    url(r'^geselecteerd/(?P<selected>[^/]*)/$',
        BookmarkedMeasuresView.as_view(),
        name='lizard_blockbox.bookmarked_measures'),
    # url(r'^table/$',
    #     BlockboxView.as_view(
    #         template_name='lizard_blockbox/blockbox-table.html'),
    #     name='lizard_blockbox_table'),
    url(r'^toggle_measure/$',
        'lizard_blockbox.views.toggle_measure',
        name='lizard_blockbox_toggle_measure'),
    url(r'^select_river/$',
        'lizard_blockbox.views.select_river',
        name='lizard_blockbox_select_river'),
    url(r'^select_year/$',
        'lizard_blockbox.views.select_year',
        name='lizard_blockbox_select_year'),
    url(r'(?P<measure>[\w\-,+]+)/pdf/$',
        'lizard_blockbox.views.fetch_factsheet',
        name="measure_factsheet"),
    url(r'^api/measures/calculated/$',
        'lizard_blockbox.views.calculated_measures_json',
        name="calculated_measures_json"),
    url(r'^api/vertex/list/$',
        'lizard_blockbox.views.vertex_json',
        name='lizard_blockbox_vertex_list'),
    url(r'^select_vertex/$',
        'lizard_blockbox.views.select_vertex',
        name='lizard_blockbox_select_vertex'),
)
urlpatterns += debugmode_urlpatterns()
