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
        # The first sheet has general information about the strategies.
        map(self.parse_sheet, wb.sheets()[1:])

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        # First two rows are not vertexes.
        row0 = sheet.row_values(1)[2:]
        vertexes = []
        for vertex in row0:
            vertex = vertex.strip()
            header = ''
            if ':' in vertex:
                # A vertex can contain multiple colons, only the
                # first one is the header
                text = vertex.split(':')
                # The header and the vertex can contain superfluous spaces.
                header = text[0].strip()
                vertex = ':'.join(text[1:]).strip()
            instance, _ = models.Vertex.objects.get_or_create(
                header=header, name=vertex)
            vertexes.append(instance)

        vertexes = dict(enumerate(vertexes, 2))

        for row_nr in xrange(2, sheet.nrows):

            row = sheet.row_values(row_nr)
            reach = models.Reach.objects.get(slug=row[1].strip())
            riversegment, _ = models.RiverSegment.objects.get_or_create(
                location=row[0], reach=reach)

            models.ReferenceValue.objects.get_or_create(
                riversegment=riversegment,
                defaults={'reference': row[2]})

            for col_nr, vertex in vertexes.iteritems():
                value = row[col_nr]
                if not value:
                    continue
                models.VertexValue.objects.get_or_create(
                    riversegment=riversegment,
                    vertex=vertex,
                    defaults={'value': value})
