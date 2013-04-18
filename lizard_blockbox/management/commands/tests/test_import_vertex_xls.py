# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

"""Tests for the import_vertex_xls command. """

# Python 3 is coming
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from django.test import TestCase

from lizard_blockbox import models
from lizard_blockbox.tests import factories
from lizard_blockbox.management.commands import import_vertex_xls

COMMAND = import_vertex_xls.Command()


class TestBuildVertexDict(TestCase):
    def test_build_vertex_dict_creates_vertices(self):
        row_values = ["Some name", "Some other name"]

        COMMAND.build_vertex_dict(row_values)

        self.assertEquals(models.Vertex.objects.count(), 2)

    def test_header_no_columns_works_correctly(self):
        row_values = ["Some name"]
        vertices = COMMAND.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEquals(vertex.header, '')
        self.assertEquals(vertex.name, 'Some name')
        self.assertEquals(vertex.year, '2100')

    def test_header_only_year_works_correctly(self):
        row_values = ["2050: Some name"]
        vertices = COMMAND.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEquals(vertex.header, '')
        self.assertEquals(vertex.name, 'Some name')
        self.assertEquals(vertex.year, '2050')

    def test_header_only_header_works_correctly(self):
        row_values = ["Whee: Some name"]
        vertices = COMMAND.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEquals(vertex.header, 'Whee')
        self.assertEquals(vertex.name, 'Some name')
        self.assertEquals(vertex.year, '2100')

    def test_header_year_and_header_works_correctly(self):
        row_values = ["2050: Whee: Some name"]
        vertices = COMMAND.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEquals(vertex.header, 'Whee')
        self.assertEquals(vertex.name, 'Some name')
        self.assertEquals(vertex.year, '2050')


class TestImportRow(TestCase):
    def test_saves_year_correctly(self):
        vertex = factories.VertexFactory.create()
        vertex.year = "2050"

        vertices = {2: vertex}

        reach = factories.ReachFactory.create(slug="MA")
        riversegment = factories.RiverSegmentFactory(
            location=1, reach=reach)

        COMMAND.import_row(vertices, [1.0, "MA", 5])

        vertex_value = models.VertexValue.objects.get(
            riversegment=riversegment,
            vertex=vertex,
            year="2050")

        self.assertEquals(vertex_value.value, 5)

