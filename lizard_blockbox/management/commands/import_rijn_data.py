from django.core.management.base import BaseCommand
from django.utils import simplejson as json

from lizard_blockbox import models
from lizard_map.coordinates import transform_point


class Command(BaseCommand):
    args = '<geojson geojson ...>'
    help = "Imports the rijntakken geojson file"

    def handle(self, *args, **options):
        map(self.parse, args)

    def parse(self, json_file):
        data = json.load(open(json_file, 'rb'))
        features = data['features']
        for feature in features:
            properties = feature['properties']
            reach_name = properties["KENMERK"]
            location, reach_slug = properties["MODELKM"].split('_')

            # Use a kilometer resolution.
            location = float(location)
            if not location.is_integer():
                continue

            x, y = feature["geometry"]["coordinates"][0]
            the_geom = transform_point(
                x, y, from_proj='google', to_proj='wgs84')

            reach, _ = models.Reach.objects.get_or_create(
                name=reach_name, slug=reach_slug)

            models.RiverSegment.objects.create(
                location=location, the_geom=the_geom, reach=reach)
