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
            for model in ('RiverSegment', 'FloodingChance', 'Measure',
                          'ReferenceValue', 'WaterLevelDifference',
                          'Reach', 'NamedReach', 'SubsetReach',
                          'CityLocation', 'Vertex', 'VertexValue'):
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
            #print 'This measure already exists: %s' % sheet.name
            return
        #print 'New measure: %s' % sheet.name
        # Flooding chance is always T1250, except for some parts of the Maas.
        flooding_T1250, _ = models.FloodingChance.objects.get_or_create(
            name='T1250')
        for row_nr in xrange(1, sheet.nrows):
            location, reference, _, difference, reach_slug = \
                sheet.row_values(row_nr)

            reach, _ = models.Reach.objects.get_or_create(slug=reach_slug)

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
                riversegment, _ = models.RiverSegment.objects.get_or_create(
                    location=location, reach=reach)
            except:
                print 'This location does not exist: %i %s' % (
                    location, reach_slug)
                continue

            ref_val, _ = models.ReferenceValue.objects.get_or_create(
                riversegment=riversegment,
                flooding_chance=flooding_T1250,
                defaults={'reference': reference})

            models.WaterLevelDifference.objects.create(
                riversegment=riversegment,
                measure=measure,
                flooding_chance=flooding_T1250,
                reference_value=ref_val,
                level_difference=difference,
                )
