import sys
import xlrd

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the measure excelfile, "
            "use --flush to flush the previous imports.")

    option_list = BaseCommand.option_list + (
        make_option('--flush',
                    action='store_true',
                    dest='flush',
                    default=False,
                    help='Flush all blockbox models for a clean import'),
        )

    def handle(self, *args, **options):
        flush = options['flush']
        if flush:
            # Delete all objects from models.
            for model in ('RiverSegment', 'Measure',
                          'ReferenceValue', 'WaterLevelDifference',
                          'Reach', 'NamedReach', 'SubsetReach',
                          'CityLocation', 'Vertex', 'VertexValue'
                          'Trajectory'):
                getattr(models, model).objects.all().delete()

        if len(args) == 0:
            if not flush:
                print "Pass excel files as arguments."
                sys.exit(1)
            sys.exit(0)

        map(self.parse, args)

    def parse(self, excel):
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        measure, created = models.Measure.objects.get_or_create(
            short_name=sheet.name)
        if not created:
            # Measure exists.
            return
        for row_nr in xrange(1, sheet.nrows):
            location, reference, _, difference, reach_slug = \
                sheet.row_values(row_nr)

            reach = models.Reach.objects.get(slug=reach_slug)

            #The Meuse has both North and South (Z) kilometers with the same
            #kilometer identifier.
            #XXX: ToDo 68_N > 68, 69_N > 68.5, 68_Z -> 69, 69_Z -> 69.5
            if isinstance(location, basestring):
                if not location.endswith('_N'):
                    # Take only the North reaches for Now
                    continue
                else:
                    location = float(location.strip('_N'))

            if not location.is_integer():
                continue
            try:
                riversegment = models.RiverSegment.objects.get(
                    location=location, reach=reach)
            except models.RiverSegment.DoesNotExist:
                print 'This location does not exist: %i %s' % (
                    location, reach_slug)
                continue

            ref_val = models.ReferenceValue.objects.get(
                riversegment=riversegment)

            models.WaterLevelDifference.objects.create(
                riversegment=riversegment,
                measure=measure,
                reference_value=ref_val,
                level_difference=difference,
                )
