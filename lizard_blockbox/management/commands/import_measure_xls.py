from optparse import make_option
import logging
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
import xlrd

from lizard_blockbox import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the measure excelfile, "
            "use --flush to flush the previous imports.")

    option_list = BaseCommand.option_list + (
        make_option('--flush',
                    action='store_true',
                    dest='flush',
                    default=False,
                    help='Flush all blockbox models for a clean import'),)

    def handle(self, *args, **options):
        flush = options['flush']
        if flush:
            # Delete all objects from models.
            for model in ('RiverSegment', 'Measure',
                          'WaterLevelDifference',
                          'Reach', 'NamedReach', 'SubsetReach',
                          'CityLocation', 'Vertex', 'VertexValue',
                          'Trajectory'):
                getattr(models, model).objects.all().delete()

        if len(args) == 0:
            if not flush:
                print "Pass excel files as arguments."
                sys.exit(1)
            sys.exit(0)

        map(self.parse, args)

    def parse(self, excel):

        def exception_parse(sheet):
            try:
                self.parse_sheet(sheet)
            except Exception:
                # Bare except due to a possible multitude in errors in the
                # provided data
                logger.exception("Error in file %s in sheet %s",
                                 excel, sheet.name)
                sys.exit(2)

        wb = xlrd.open_workbook(excel)
        map(exception_parse, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        short_name = sheet.name
        if isinstance(short_name, float):
            short_name = int(short_name)
        measure, created = models.Measure.objects.get_or_create(
            short_name=short_name)

        if not created:
            # Measure exists.
            return
        for row_nr in xrange(1, sheet.nrows):
            self.parse_row(measure, sheet.row_values(row_nr))

    def parse_row(self, measure, row_values):
        # Row has either 5 or 6 values; make sure it has 6
        row_values = (tuple(row_values) + (None,))[:6]

        (location, _, _, difference, reach_slug, difference_250) =\
            row_values

        try:
            reach = models.Reach.objects.get(slug=reach_slug)
        except models.Reach.DoesNotExist:
            raise ValueError("Reach with slug=%r not found" % reach_slug)

        #The Meuse has both North and South (Z) kilometers with the same
        #kilometer identifier.
        #XXX: ToDo 68_N > 68, 69_N > 68.5, 68_Z -> 69, 69_Z -> 69.5
        if isinstance(location, basestring):
            if not location.endswith('_N'):
                # Take only the North reaches for Now
                return
            else:
                location = float(location.strip('_N'))

        # We only use the values at integer kilometer marks
        if not location.is_integer():
            return

        try:
            riversegment = models.RiverSegment.objects.get(
                location=location, reach=reach)
        except models.RiverSegment.DoesNotExist:
            print 'This location does not exist: %i %s' % (
                location, reach_slug)
            return

        models.WaterLevelDifference.objects.create(
            riversegment=riversegment,
            measure=measure,
            protection_level="1250",
            level_difference=difference,
            )

        if difference_250 is not None:
            models.WaterLevelDifference.objects.create(
                riversegment=riversegment,
                measure=measure,
                protection_level="250",
                level_difference=difference_250,
                )
