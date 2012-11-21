import sys

import xlrd

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the measures table excelfile, "
            "To flush use the management command: import_measure_xls --flush")

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Pass excel files as arguments."
            sys.exit(1)

        map(self.parse, args)

    def parse(self, excel):
        def exception_parse(sheet):
            try:
                self.parse_sheet(sheet)
            except Exception:
                # Bare except due to a possible multitude in errors in the
                # provided data
                print "There is an error at the following place:"
                print "Filename: {}".format(excel)
                print "Sheet: {}".format(sheet.name)
                raise
                sys.exit(2)

        wb = xlrd.open_workbook(excel)
        map(exception_parse, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        col_names = (
            'name', 'short_name', 'measure_type', 'km_from', 'km_to',
            'reach', 'riverpart', 'mhw_profit_cm', 'mhw_profit_m2',
            'investment_costs', 'life_costs', 'total_costs', 'investment_m2')

        col_index = dict(zip(col_names, xrange(len(col_names))))

        for row_nr in xrange(1, sheet.nrows):
            row_values = sheet.row_values(row_nr)
            short_name = row_values[col_index['short_name']]

            if isinstance(short_name, float):
                # Integers are read as floats, so integerize them.
                row_values[col_index['short_name']] = int(short_name)

            default_values = dict(zip(col_names, row_values))
            default_values['reach'], _ = models.Reach.objects.get_or_create(
                slug=default_values['reach'])
            measure, _ = models.Measure.objects.get_or_create(
                short_name=row_values[col_index['short_name']])

            # km_from and km_to are integers.
            # DB save doesnt automatically converted '' to None.
            for item in ('km_from', 'km_to'):
                if default_values[item] == '':
                    default_values[item] = None

            models.Measure.objects.filter(id=measure.id).update(
                **default_values)
