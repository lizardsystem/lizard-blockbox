# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

"""Tests for the import_measure_xls command"""

# Python 3 is coming
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import mock
import sys
from io import StringIO

from django.test import TestCase

from lizard_blockbox.tests import factories
from lizard_blockbox import models

from lizard_blockbox import import_helpers


class TestImportMeasureXls(TestCase):
    def test_row_with_five_values_saves_correct_difference(self):
        measure = factories.MeasureFactory.create()
        reach = factories.ReachFactory.create(slug="reach_slug")
        factories.RiverSegmentFactory.create(location=1.0, reach=reach)

        row = [1.0, 55.0, None, -1, "reach_slug"]

        import_helpers.import_measure_row(measure, row, rownr=0, stdout=sys.stdout)

        self.assertEqual(models.WaterLevelDifference.objects.all().count(), 1)
        diff = models.WaterLevelDifference.objects.all()[0]
        self.assertEqual(diff.protection_level, "1250")
        self.assertEqual(diff.level_difference, -1)

    def test_row_with_six_values_saves_correct_difference(self):
        measure = factories.MeasureFactory.create()
        reach = factories.ReachFactory.create(slug="reach_slug")
        factories.RiverSegmentFactory.create(location=1.0, reach=reach)

        row = [1.0, 55.0, None, -3, "reach_slug", -4]

        import_helpers.import_measure_row(measure, row, rownr=0, stdout=sys.stdout)

        self.assertEqual(models.WaterLevelDifference.objects.all().count(), 2)

        diff_1250 = models.WaterLevelDifference.objects.filter(protection_level="1250")[
            0
        ]
        self.assertEqual(diff_1250.level_difference, -3)

        diff_250 = models.WaterLevelDifference.objects.filter(protection_level="250")[0]
        self.assertEqual(diff_250.level_difference, -4)


class TestBuildVertexDict(TestCase):
    def test_build_vertex_dict_creates_vertices(self):
        row_values = ["Some name", "Some other name"]

        import_helpers.build_vertex_dict(row_values)

        self.assertEqual(models.Vertex.objects.count(), 2)

    def test_header_no_columns_works_correctly(self):
        row_values = ["Some name"]
        vertices = import_helpers.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEqual(vertex.header, "")
        self.assertEqual(vertex.name, "Some name")
        self.assertEqual(vertex.year, "2100")

    def test_header_only_year_works_correctly(self):
        row_values = ["2050: Some name"]
        vertices = import_helpers.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEqual(vertex.header, "")
        self.assertEqual(vertex.name, "Some name")
        self.assertEqual(vertex.year, "2050")

    def test_header_only_header_works_correctly(self):
        row_values = ["Whee: Some name"]
        vertices = import_helpers.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEqual(vertex.header, "Whee")
        self.assertEqual(vertex.name, "Some name")
        self.assertEqual(vertex.year, "2100")

    def test_header_year_and_header_works_correctly(self):
        row_values = ["2050: Whee: Some name"]
        vertices = import_helpers.build_vertex_dict(row_values)
        vertex = vertices[2]
        self.assertEqual(vertex.header, "Whee")
        self.assertEqual(vertex.name, "Some name")
        self.assertEqual(vertex.year, "2050")


class TestImportVertexXls(TestCase):
    def test_saves_year_correctly(self):
        vertex = factories.VertexFactory.create()
        vertex.year = "2050"

        vertices = {2: vertex}

        reach = factories.ReachFactory.create(slug="MA")
        riversegment = factories.RiverSegmentFactory(location=1, reach=reach)

        import_helpers.import_vertex_row(vertices, [1.0, "MA", 5])

        vertex_value = models.VertexValue.objects.get(
            riversegment=riversegment, vertex=vertex, year="2050"
        )

        self.assertEqual(vertex_value.value, 5)

    def test_saves_column_after_empty_column(self):
        vertex1 = factories.VertexFactory.create()
        vertex2 = factories.VertexFactory.create()
        vertex1.year = "2050"
        vertex2.year = "2050"

        vertices = {2: vertex1, 3: vertex1, 4: vertex2}

        reach = factories.ReachFactory.create(slug="MA")
        riversegment = factories.RiverSegmentFactory(location=1, reach=reach)

        import_helpers.import_vertex_row(vertices, [1.0, "MA", 1.0, "", 2.0])

        value1 = models.VertexValue.objects.get(
            riversegment=riversegment, vertex=vertex1, year="2050"
        )
        value2 = models.VertexValue.objects.get(
            riversegment=riversegment, vertex=vertex2, year="2050"
        )
        self.assertEqual(value1.value, 1.0)
        self.assertEqual(value2.value, 2.0)


class TestMapOverSheets(TestCase):
    def test_reraises_with_excelpath_sheetname(self):
        path = "/some/excelpath"
        mocked_sheet = mock.MagicMock()
        mocked_sheet.name = "sheetname"
        sheets = [mocked_sheet]

        workbook = mock.MagicMock()
        workbook.sheets.return_value = sheets

        fake_stdout = StringIO()

        def called_function(sheet, stdout):
            self.assertTrue(sheet is mocked_sheet)
            self.assertTrue(stdout is fake_stdout)
            raise import_helpers.ExcelException(error="some error")

        with mock.patch("xlrd.open_workbook", return_value=workbook) as patched_open:
            try:
                import_helpers.map_over_sheets(path, called_function, fake_stdout)

                # We shouldn't get here, so this fails if we do
                self.assertRaises(Exception, lambda: None)
            except import_helpers.ExcelException as ee:
                self.assertEqual(ee.path, path)
                self.assertEqual(ee.sheet, "sheetname")
                self.assertEqual(ee.rownr, None)
                self.assertEqual(ee.error, "some error")

            patched_open.assert_called_with(path)
