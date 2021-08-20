from django.urls import re_path
from lizard_map import views


urlpatterns = [
    # Load and save map location
    re_path(
        r"^map_location_save$",
        views.map_location_save,
        name="lizard_map.map_location_save",
    ),
    re_path(
        r"^map_location_load_default$",
        views.map_location_load_default,
        name="lizard_map.map_location_load_default",
    ),
]
