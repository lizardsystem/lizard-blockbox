from django.core.management.base import BaseCommand
from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = "Fetch the data from the ftp server."

    def handle(self, *args, **kwargs):
        import_helpers.fetch_blockbox_data(self.stdout)
