import sys

import xlrd

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the excluding measurements excelfile, "
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
            measure, excluding = sheet.row_values(row_nr)
            excludes = [i.strip() for i in excluding.split(';')]
            try:
                measure = models.Measure.objects.get(short_name=measure)
            except models.Measure.DoesNotExist:
                continue
            for exclude in excludes:
                try:
                    instance = models.Measure.objects.get(short_name=exclude)
                except models.Measure.DoesNotExist:
                    continue
                measure.exclude.add(instance)
                measure.save()
