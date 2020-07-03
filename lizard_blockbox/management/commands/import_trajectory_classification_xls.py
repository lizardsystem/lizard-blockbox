import sys

from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers


class Command(BaseCommand):
    help = ("Imports the trajectory classifications excelfile, "
            "To flush use the management command: import_measure_xls --flush")

    def add_arguments(self, parser):
        parser.add_argument('excelfile', nargs='+')

    def handle(self, *args, **options):
        if not options.get('excelfile', None):
            print("Pass excel files as arguments.")
            sys.exit(1)

        self.stdout.write("Import trajectindeling...\n")
        for excelpath in options['excelfile']:
            import_helpers.parse_trajectory_classification_excelfile(
                excelpath, self.stdout)
