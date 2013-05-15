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
        # The first row (0) of the sheet contains irrelevant comments;
        # the first two columns are always location and reach. So
        # we're interested in the headers in the rest of the 2nd row:
        vertices = self.build_vertex_dict(sheet.row_values(1)[2:])

        # Then, for every row after the first two, import it
        for row_nr in xrange(2, sheet.nrows):
            self.import_row(vertices, sheet.row_values(row_nr))

    def build_vertex_dict(self, row_values):
        vertices = []

        for vertex in row_values:
            vertex = vertex.strip()
            header = ''
            year = "2100"  # Let's use a default in case we don't find a year

            # The first part of the vertex should be the year
            if ':' in vertex:
                parts = vertex.split(':')
                first_part = parts[0].strip()
                if first_part in models.VertexValue.YEARS:
                    year = first_part
                    vertex = ':'.join(parts[1:]).strip()

            # Process the rest, which may contain a header
            if ':' in vertex:
                # A vertex can contain multiple colons, only the
                # first one is the header
                text = vertex.split(':')
                # The header and the vertex can contain superfluous spaces.
                header = text[0].strip()
                vertex = ':'.join(text[1:]).strip()
            instance, _ = models.Vertex.objects.get_or_create(
                header=header, name=vertex)

            instance.year = year  # Not saved on this model! But this
                                  # is a convenient place to keep the
                                  # variable around for below

            vertices.append(instance)

        return dict(enumerate(vertices, 2))

    def import_row(self, vertices, row):
        # Skip unused slug 'ST' (Steurgat)
        if row[1].strip() == 'ST':
            return

        reach = models.Reach.objects.get(slug=row[1].strip())

        riversegment, _ = models.RiverSegment.objects.get_or_create(
            location=row[0], reach=reach)

        for col_nr, vertex in vertices.iteritems():
            value = row[col_nr]
            if not value:
                continue  # Skip this column, but there may still be
                          # data in later columns
            models.VertexValue.objects.get_or_create(
                riversegment=riversegment,
                vertex=vertex,
                year=vertex.year,  # Set the year we saved above
                defaults={'value': value})
