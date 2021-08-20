# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.urls import re_path
from lizard_blockbox import views
from lizard_blockbox.views import BlockboxView
from lizard_blockbox.views import BookmarkedMeasuresView
from lizard_blockbox.views import SelectedMeasuresView
from lizard_ui.urls import debugmode_urlpatterns


urlpatterns = [
    re_path(r"^$", BlockboxView.as_view(), name="lizard_blockbox.home"),
    re_path(r"^csv/$", views.generate_csv, name="lizard_blockbox.generate_csv"),
    re_path(
        r"^data/measures/excluding/$",
        views.download_data,
        kwargs={
            "file": (
                "excelsheets",
                "elkaar uitsluitende maatregelen",
                "Maatregelen die elkaar uitsluiten.xls",
            )
        },
        name="lizard_blockbox.excluding_measures",
    ),
    re_path(
        r"^geselecteerd/$",
        SelectedMeasuresView.as_view(),
        name="lizard_blockbox.selected_measures",
    ),
    re_path(
        r"^bookmark/$",
        BookmarkedMeasuresView.as_view(),
        name="lizard_blockbox.bookmarked_measures",
    ),
    # re_path(r'^table/$',
    #     BlockboxView.as_view(
    #         template_name='lizard_blockbox/blockbox-table.html'),
    #     name='lizard_blockbox_table'),
    re_path(
        r"^toggle_measure/$",
        views.toggle_measure,
        name="lizard_blockbox_toggle_measure",
    ),
    re_path(r"^select_river/$", views.select_river, name="lizard_blockbox_select_river"),
    re_path(r"^select_year/$", views.select_year, name="lizard_blockbox_select_year"),
    re_path(
        r"(?P<measure>[\w\-,+]+)/pdf/$", views.fetch_factsheet, name="measure_factsheet"
    ),
    re_path(
        r"^api/measures/calculated/$",
        views.calculated_measures_json,
        name="calculated_measures_json",
    ),
    re_path(r"^api/vertex/list/$", views.vertex_json, name="lizard_blockbox_vertex_list"),
    re_path(r"^select_vertex/$", views.select_vertex, name="lizard_blockbox_select_vertex"),
    re_path(
        r"^api/protection_level/list/$",
        views.protection_level_json,
        name="lizard_blockbox_protection_level_list",
    ),
    # re_path(r'^select_protection_level/$',
    #     'lizard_blockbox.views.select_protection_level',
    #     name='lizard_blockbox_select_protection_level'),
]
urlpatterns += debugmode_urlpatterns()
