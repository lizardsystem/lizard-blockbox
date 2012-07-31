# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxView
from lizard_blockbox.views import ReportMapView
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
            # url(r'^s/(?P<width>[\d]+)x(?P<height>[\d]+)/(?P<url>.+)/$', DirectImageView),
    # url(r'^report/map/(?P<session_slug>.+)/$',
    #     'lizard_blockbox.views.report_map_template',
    #     name='lizard_blockbox.report_map_template'),
    url(r'^report/map/(?P<session_slug>.+)/$',
        ReportMapView.as_view(),
        name='lizard_blockbox.report_map_template'),
    url(r'^csv/$',
        'lizard_blockbox.views.generate_csv',
        name='lizard_blockbox.generate_csv'),
    url(r'^geselecteerd/$',
        SelectedMeasuresView.as_view(),
        name='lizard_blockbox.selected_measures'),
    url(r'^geselecteerd/(?P<selected>[^/]*)/$',
        BookmarkedMeasuresView.as_view(),
        name='lizard_blockbox.bookmarked_measures'),
    url(r'^table/$',
        BlockboxView.as_view(
            template_name='lizard_blockbox/blockbox-table.html'),
        name='lizard_blockbox_table'),
    url(r'^toggle_measure/$',
        'lizard_blockbox.views.toggle_measure',
        name='lizard_blockbox_toggle_measure'),
    url(r'^select_river/$',
        'lizard_blockbox.views.select_river',
        name='lizard_blockbox_select_river'),
    url(r'(?P<measure>[\w\-,]+)/pdf/$',
        'lizard_blockbox.views.fetch_factsheet',
        name="measure_factsheet"),
    url(r'^api/measures/calculated/$',
        'lizard_blockbox.views.calculated_measures_json',
        name="calculated_measures_json"),
    url(r'^api/measures/list/$',
        'lizard_blockbox.views.list_measures_json',
        name="measure_list_json"),
    url(r'^api/city_locations/json/$',
        'lizard_blockbox.views.city_locations_json',
        name='city_list_json'),
    url(r'^api/vertex/list/$',
        'lizard_blockbox.views.vertex_json',
        name='lizard_blockbox_vertex_list'),
    url(r'^select_vertex/$',
        'lizard_blockbox.views.select_vertex',
        name='lizard_blockbox_select_vertex'),
)
urlpatterns += debugmode_urlpatterns()
