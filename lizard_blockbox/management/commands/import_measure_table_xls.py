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
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        col_names = (
            'name', 'short_name',  'measure_type', 'km_from', 'km_to',
            'reach', 'riverpart', 'mhw_profit_cm', 'mhw_profit_m2',
            'investment_costs', 'benefits', 'b_o_costs', 'reinvestment',
            'damage', 'total_costs', 'quality_of_environment'
            )

        col_index = dict(zip(col_names, xrange(len(col_names))))

        for row_nr in xrange(1, sheet.nrows):
            row_values = sheet.row_values(row_nr)
            default_values = dict(zip(col_names, row_values))
            default_values['reach'], _ = models.Reach.objects.get_or_create(
                slug=default_values['reach'],
                defaults={'name': default_values['reach']})
            measure, _ = models.Measure.objects.get_or_create(
                short_name=row_values[col_index['short_name']])

            for k, v in default_values.iteritems():
                try:
                    setattr(measure, k, v)
                    measure.save()
                except Exception, e:
                    import ipdb; ipdb.set_trace()


