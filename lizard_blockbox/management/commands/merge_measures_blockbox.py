from django.core.management.base import BaseCommand
from lizard_blockbox import import_helpers


class Command(BaseCommand):
    args = ""
    help = "Merge the measure shapes to get one json."

    def handle(self, *args, **kwargs):
        import_helpers.merge_measures_blockbox(self.stdout)
