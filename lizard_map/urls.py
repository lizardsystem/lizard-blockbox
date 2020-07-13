from django.conf.urls import url
from lizard_map import views

urlpatterns = [
    # Load and save map location
    url(
        r"^map_location_save$",
        views.map_location_save,
        name="lizard_map.map_location_save",
    ),
    url(
        r"^map_location_load_default$",
        views.map_location_load_default,
        name="lizard_map.map_location_load_default",
    ),
]
