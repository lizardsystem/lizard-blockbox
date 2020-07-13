from django.core.management.base import BaseCommand
from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = "Simplify kilometers shape."

    def handle(self, *args, **kwargs):
        import_helpers.parse_kilometers_json(self.stdout)
