# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls import include, url

from lizard_ui.urls import debugmode_urlpatterns
from lizard_blockbox.views import BlockboxView
from lizard_blockbox.views import SelectedMeasuresView
from lizard_blockbox.views import BookmarkedMeasuresView
from lizard_blockbox import views

urlpatterns = [
    url(r'^$',
        BlockboxView.as_view(),
        name='lizard_blockbox.home'),
    url(r'^csv/$',
        views.generate_csv,
        name='lizard_blockbox.generate_csv'),
    url(r'^data/measures/excluding/$',
        views.download_data,
        kwargs={'file': ('excelsheets', 'elkaar uitsluitende maatregelen',
                'Maatregelen die elkaar uitsluiten.xls')},
        name='lizard_blockbox.excluding_measures'),
    url(r'^geselecteerd/$',
        SelectedMeasuresView.as_view(),
        name='lizard_blockbox.selected_measures'),
    url(r'^bookmark/$',
        BookmarkedMeasuresView.as_view(),
        name='lizard_blockbox.bookmarked_measures'),
    # url(r'^table/$',
    #     BlockboxView.as_view(
    #         template_name='lizard_blockbox/blockbox-table.html'),
    #     name='lizard_blockbox_table'),
    url(r'^toggle_measure/$',
        views.toggle_measure,
        name='lizard_blockbox_toggle_measure'),
    url(r'^select_river/$',
        views.select_river,
        name='lizard_blockbox_select_river'),
    url(r'^select_year/$',
        views.select_year,
        name='lizard_blockbox_select_year'),
    url(r'(?P<measure>[\w\-,+]+)/pdf/$',
        views.fetch_factsheet,
        name="measure_factsheet"),
    url(r'^api/measures/calculated/$',
        views.calculated_measures_json,
        name="calculated_measures_json"),
    url(r'^api/vertex/list/$',
        views.vertex_json,
        name='lizard_blockbox_vertex_list'),
    url(r'^select_vertex/$',
        views.select_vertex,
        name='lizard_blockbox_select_vertex'),
    url(r'^api/protection_level/list/$',
        views.protection_level_json,
        name='lizard_blockbox_protection_level_list'),
    # url(r'^select_protection_level/$',
    #     'lizard_blockbox.views.select_protection_level',
    #     name='lizard_blockbox_select_protection_level'),

    # Automatic imports
    url(r'^import/$',
        views.AutomaticImportPage.as_view(),
        name="lizard_blockbox.automatic_import"),
    url(r'^import/(?P<command>\w+)/$',
        views.AutomaticImportPage.as_view(),
        name="lizard_blockbox.automatic_import_command"),
    url(r'^allimport/',
        include('lizard_management_command_runner.urls'))
]
urlpatterns += debugmode_urlpatterns()
