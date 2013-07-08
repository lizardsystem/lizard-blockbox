from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers


class Command(BaseCommand):
    args = ''
    help = ("Copy the geojson shape files to the static directory for Django")

    def handle(self, *args, **kwargs):
        import_helpers.copy_json_to_blockbox(self.stdout)
