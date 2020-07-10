import json

from django.core.management.base import BaseCommand

from lizard_blockbox import models


class Command(BaseCommand):
    help = "Imports the measure geojson file"

    def add_arguments(self, parser):
        parser.add_argument("geojson", nargs="+")

    def handle(self, *args, **options):
        map(self.parse, options["geojson"])

    def parse(self, json_file):
        data = json.load(open(json_file, "rb"))
        features = data["features"]
        for feature in features:
            properties = feature["properties"]
            # Parse code key dynamically
            # Key can be Code_IVM or Code_QS, or something else.
            short_name_key = [
                i for i in properties.keys() if i.lower().startswith("code")
            ][0]

            # Parse and save the properties
            try:
                measure = models.Measure.objects.get(
                    short_name=properties[short_name_key]
                )
            except models.Measure.DoesNotExist:
                # print 'Measure not found: %s' % properties[short_name_key]
                continue
            else:
                # print 'Found: %s' % properties[short_name_key]
                measure.name = properties["titel"]
                measure.measure_type = properties["type"]
                measure.traject = properties["traject"]
                # XXX: Be aware that the River Reach must be coupled with
                # the measure
                measure.km_from = int(round(properties["km_van"]))
                measure.km_to = int(round(properties["km_tot"]))
                measure.save()
