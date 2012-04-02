import xlrd

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = "Imports the measure excelfile."

    def handle(self, *args, **options):
        map(self.parse, (i for i in args))

    def parse(self, excel):
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        year = models.Year.objects.get_or_create(year=2050)
        scenario = models.Scenario.objects.get_or_create(name='Stoom')
        measure = models.Measure(short_name=sheet.name)
        measure.save()
        # variables that are not variables for now
        year = models.Year.objects.get_or_create(year=2150)[0]
        scenario = models.Scenario.objects.get_or_create(name='Stoom')[0]

        flooding_T250 = models.FloodingChance.objects.get_or_create(
            name='T250')[0]
        flooding_T1250 = models.FloodingChance.objects.get_or_create(
            name='T1250')[0]

        for row_nr in xrange(1, sheet.nrows):
            row = sheet.row_values(row_nr)
            location = row[0]
            # Only use a kilomter resolution, which are integers
            if not location.is_integer():
                continue
            riversegment = models.RiverSegment.objects.get_or_create(
                location=row[0])[0]
            chances = ((flooding_T250, 3, 7), (flooding_T1250, 4, 8))
            for chance in chances:
                d = {'riversegment': riversegment,
                     'scenario': scenario,
                     'year': year,
                     'flooding_chance': chance[0]}
                #target is -1 to just have a target that's different from
                #the reference value.
                models.ReferenceValue.objects.get_or_create(
                    reference=row[chance[1]],
                    target=row[chance[1]] - 1,
                    **d)
                d['measure'] = measure
                models.Delta.objects.create(
                    delta=row[chance[2]],
                    **d)
