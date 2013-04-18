# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

"""Tests for models.py"""

# Python 3 is coming
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from django.test import TestCase

from lizard_blockbox.tests import factories


class TestNamedReach(TestCase):
    def test_protection_levels_within_subsetreach(self):
        namedreach = factories.NamedReachFactory.create()
        reach = factories.ReachFactory.create()

        factories.SubsetReachFactory.create(
            reach=reach, named_reach=namedreach,
            km_from=1, km_to=100)

        segment = factories.RiverSegmentFactory(
            location=50, reach=reach)

        measure = factories.MeasureFactory.create()

        factories.WaterLevelDifferenceFactory.create(
            riversegment=segment, measure=measure, protection_level="1250")
        factories.WaterLevelDifferenceFactory.create(
            riversegment=segment, measure=measure, protection_level="250")

        self.assertEquals(namedreach.protection_levels, ["250", "1250"])

    def test_250_doesnt_occur(self):
        namedreach = factories.NamedReachFactory.create()
        reach = factories.ReachFactory.create()

        factories.SubsetReachFactory.create(
            reach=reach, named_reach=namedreach,
            km_from=1, km_to=100)

        segment = factories.RiverSegmentFactory(
            location=50, reach=reach)

        measure = factories.MeasureFactory.create()

        factories.WaterLevelDifferenceFactory.create(
            riversegment=segment, measure=measure, protection_level="1250")

        self.assertEquals(namedreach.protection_levels, ["1250"])

    def test_250_occurs_outside_of_km_from_to(self):
        namedreach = factories.NamedReachFactory.create()
        reach = factories.ReachFactory.create()

        factories.SubsetReachFactory.create(
            reach=reach, named_reach=namedreach,
            km_from=1, km_to=100)

        segment = factories.RiverSegmentFactory(
            location=150, reach=reach)

        measure = factories.MeasureFactory.create()

        factories.WaterLevelDifferenceFactory.create(
            riversegment=segment, measure=measure, protection_level="1250")
        factories.WaterLevelDifferenceFactory.create(
            riversegment=segment, measure=measure, protection_level="250")

        self.assertEquals(namedreach.protection_levels, ["1250"])


class TestVertex(TestCase):
    def test_years(self):
        vertex = factories.VertexFactory.create()
        riversegment = factories.RiverSegmentFactory.create()

        factories.VertexValueFactory.create(
            vertex=vertex, riversegment=riversegment, year="2050")
        factories.VertexValueFactory.create(
            vertex=vertex, riversegment=riversegment, year="2050")
        factories.VertexValueFactory.create(
            vertex=vertex, riversegment=riversegment, year="2100")

        self.assertEquals(vertex.years, ["2050", "2100"])
