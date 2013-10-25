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

    def test_expanded_reaches(self):
        """If there are two trajectories -- A, B, C, D and E, F, G, H --
        and a river C, F, then it should be expanded to A, B, C, F, G, H."""
        trajectory1 = factories.TrajectoryFactory.create(name=1)
        trajectory2 = factories.TrajectoryFactory.create(name=2)

        reaches = {
            c: factories.ReachFactory.create(slug=c)
            for c in "ABCDEFGH"}
        for i, c in enumerate("ABCD"):
            reaches[c].number = i
            reaches[c].save()
            trajectory1.reach.add(reaches[c])
        for i, c in enumerate("EFGH"):
            reaches[c].number = i
            reaches[c].save()
            trajectory2.reach.add(reaches[c])

        river = factories.NamedReachFactory.create(name="test")

        factories.SubsetReachFactory.create(
            reach=reaches['C'], named_reach=river, km_from=100, km_to=200)
        factories.SubsetReachFactory.create(
            reach=reaches['F'], named_reach=river, km_from=201, km_to=300)

        expanded_reaches = river.expanded_reaches()
        self.assertEquals(len(expanded_reaches), 6)
        self.assertEquals(expanded_reaches[0].slug, 'A')
        self.assertEquals(expanded_reaches[1].slug, 'B')
        self.assertEquals(expanded_reaches[2].slug, 'C')
        self.assertEquals(expanded_reaches[3].slug, 'F')
        self.assertEquals(expanded_reaches[4].slug, 'G')
        self.assertEquals(expanded_reaches[5].slug, 'H')


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
