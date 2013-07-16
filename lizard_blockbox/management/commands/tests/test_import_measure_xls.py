# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

"""Tests for the import_measure_xls command"""

# Python 3 is coming
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


from django.test import TestCase

from lizard_blockbox.tests import factories
from lizard_blockbox import models
from lizard_blockbox.management.commands import import_measure_xls


class TestCommand(TestCase):
    def test_row_with_five_values_saves_correct_difference(self):
        measure = factories.MeasureFactory.create()
        reach = factories.ReachFactory.create(slug="reach_slug")
        factories.RiverSegmentFactory.create(location=1.0, reach=reach)

        row = [1.0, 55.0, None, -1, "reach_slug"]

        command = import_measure_xls.Command()

        command.parse_row(measure, row, rownr=0)

        self.assertEquals(
            models.WaterLevelDifference.objects.all().count(),
            1)
        diff = models.WaterLevelDifference.objects.all()[0]
        self.assertEquals(diff.protection_level, "1250")
        self.assertEquals(diff.level_difference, -1)

    def test_row_with_six_values_saves_correct_difference(self):
        measure = factories.MeasureFactory.create()
        reach = factories.ReachFactory.create(slug="reach_slug")
        factories.RiverSegmentFactory.create(location=1.0, reach=reach)

        row = [1.0, 55.0, None, -3, "reach_slug", -4]

        command = import_measure_xls.Command()

        command.parse_row(measure, row, rownr=0)

        self.assertEquals(
            models.WaterLevelDifference.objects.all().count(),
            2)

        diff_1250 = models.WaterLevelDifference.objects.filter(
            protection_level="1250")[0]
        self.assertEquals(diff_1250.level_difference, -3)

        diff_250 = models.WaterLevelDifference.objects.filter(
            protection_level="250")[0]
        self.assertEquals(diff_250.level_difference, -4)
