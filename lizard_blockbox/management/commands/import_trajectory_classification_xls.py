import sys

import xlrd

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the trajectory classifications excelfile, "
            "To flush use the management command: import_measure_xls --flush")

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Pass excel files as arguments."
            sys.exit(1)

        self.stdout.write("Import trajectindeling...\n")
        map(self.parse, args)

    def parse(self, excel):
        self.stdout.write("Parsing '{excel}'\n".format(excel=excel))
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        for row_nr in xrange(1, sheet.nrows):
            name, reach_slug, km_from, km_to = sheet.row_values(row_nr)
            km_from, km_to = int(km_from), int(km_to)
            reach, _ = models.Reach.objects.get_or_create(slug=reach_slug)
            named_reach, _ = models.NamedReach.objects.get_or_create(name=name)

            models.SubsetReach.objects.get_or_create(
                reach=reach,
                named_reach=named_reach,
                km_from=km_from,
                km_to=km_to)
