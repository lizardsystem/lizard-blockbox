from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = ("Parse the shapes for the blockbox data.")

    def handle(self, *args, **kwargs):
        import_helpers.parse_shapes_blockbox(self.stdout)
