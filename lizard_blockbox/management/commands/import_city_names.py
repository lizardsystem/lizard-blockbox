import sys

from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the city excelfile, "
            "To flush use the management command: import_measure_xls --flush")

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Pass excel files as arguments."
            sys.exit(1)

        for excelpath in args:
            import_helpers.import_city_names(excelpath, self.stdout)
