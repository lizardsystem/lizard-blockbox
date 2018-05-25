from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = ("Copy the geojson shape files to the media directory for Django")

    def handle(self, *args, **kwargs):
        import_helpers.copy_json_to_media(self.stdout)
