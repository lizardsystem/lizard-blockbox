from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = ("Run a data import using fab.")

    def handle(self, *args, **kwargs):
        """Run subcommands"""
        import_helpers.fetch_blockbox_data(self.stdout)
        import_helpers.set_permissions_pdf(self.stdout)
        import_helpers.parse_shapes_blockbox(self.stdout)
        import_helpers.parse_kilometers_json(self.stdout)
        import_helpers.merge_measures_blockbox(self.stdout)
        import_helpers.copy_json_to_media(self.stdout)
