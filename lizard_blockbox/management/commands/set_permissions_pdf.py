from django.core.management.base import BaseCommand
from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = "Set read permissions for the facsheets."

    def handle(self, *args, **kwargs):
        import_helpers.set_permissions_pdf(self.stdout)
