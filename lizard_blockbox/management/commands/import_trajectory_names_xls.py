import sys

import xlrd

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the trajectory excelfile, "
            "To flush use the management command: import_measure_xls --flush")

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Pass excel files as arguments."
            sys.exit(1)

        map(self.parse, args)

    def parse(self, excel):
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        for row_nr in xrange(1, sheet.nrows):
            name, reach_slugs, _ = sheet.row_values(row_nr)
            reaches = reach_slugs.split(', ')

            tr, _ = models.Trajectory.objects.get_or_create(name=name)
            for reach_name in reaches:
                reach = models.Reach.objects.get(slug=reach_name.strip())
                tr.reach.add(reach)
                tr.save()
