import sys

import xlrd

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_blockbox import models
from lizard_blockbox import utils


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the vertex excelfile, "
            "To flush use the management command: import_measure_xls --flush")

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Pass excel files as arguments."
            sys.exit(1)

        map(self.parse, args)
        #Link Vertexes with the NamedReaches
        for named_reach in models.NamedReach.objects.all():
            rs = utils.namedreach2riversegments(named_reach)
            vertexes = models.Vertex.objects.filter(
                vertexvalue__riversegment__in=rs).distinct()
            for vertex in vertexes:
                vertex.named_reaches.add(named_reach)
                vertex.save()

    def parse(self, excel):
        wb = xlrd.open_workbook(excel)
        map(self.parse_sheet, wb.sheets())

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        # First two rows are not vertexes.
        row0 = sheet.row_values(0)[2:]
        vertexes = [models.Vertex.objects.create(name=vertex) for
                    vertex in row0]
        vertexes = dict(enumerate(vertexes, 2))

        for row_nr in xrange(1, sheet.nrows):

            row = sheet.row_values(row_nr)
            km = row[0]
            if isinstance(km, basestring) and km[-1] in ('Z', 'N'):
                #ToDo: Parse Meuse KM with 'N' or 'Z' correctly
                continue
            try:
                riversegment = models.RiverSegment.objects.get(
                    location=row[0],
                    reach__slug=row[1])
            except models.RiverSegment.DoesNotExist:
                continue

            for col_nr, vertex in vertexes.iteritems():
                models.VertexValue.objects.create(
                    riversegment=riversegment,
                    vertex=vertex,
                    value=row[col_nr])
