import sys
import xlrd

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models
from lizard_map.coordinates import transform_point


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
                          'Reach'):
                getattr(models, model).objects.all().delete()

        if len(args) == 0:
            if not flush:
                print "Pass excel files as arguments."
                sys.exit(1)
            sys.exit(0)

        map(self.parse, args)

    def parse(self, excel):
        #print 'Workbook: %s' % excel
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        reach, _ = models.Reach.objects.get_or_create(name='Maas', slug="MA")
        measure = models.Measure.objects.create(short_name=sheet.name)
        flooding_T250, _ = models.FloodingChance.objects.get_or_create(
            name='T250')
        flooding_T1250, _ = models.FloodingChance.objects.get_or_create(
            name='T1250')

        for row_nr in xrange(1, sheet.nrows):
            row = sheet.row_values(row_nr)
            location = row[0]
            #Parse N/Z reaches for river maas, only use north.
            if isinstance(location, basestring):
                if not location.endswith('_N'):
                    # Take only the North reaches
                    continue
                else:
                    location = float(location.strip('_N'))
            # Only use a kilomter resolution, which are integers
            if not location.is_integer():
                    continue
            try:
                riversegment = models.RiverSegment.objects.get(
                    location=location, reach=reach)
            except models.RiverSegment.DoesNotExist:
                the_geom = transform_point(
                    row[1], row[2], from_proj='rd', to_proj='wgs84')
                riversegment = models.RiverSegment.objects.create(
                    location=location, the_geom=the_geom, reach=reach)
            # XXX: Named tuple?
            # Easy datastructure for the columns.
            chances = ((flooding_T250, 3, 7), (flooding_T1250, 4, 8))
            for chance in chances:
                d = {'riversegment': riversegment,
                     'flooding_chance': chance[0]}
                #Reference value can differ because
                #river segments can be defined twice.
                try:
                    ref_val = models.ReferenceValue.objects.get(
                        **d)
                except models.ReferenceValue.DoesNotExist:
                    #target is -1 to just have a target that's different from
                    #the reference value.
                    ref_val = models.ReferenceValue.objects.create(
                        reference=row[chance[1]],
                        target=row[chance[1]] - 1,
                        **d)
                d['measure'] = measure
                d['reference_value'] = ref_val
                models.WaterLevelDifference.objects.create(
                    level_difference=row[chance[2]],
                    **d)
