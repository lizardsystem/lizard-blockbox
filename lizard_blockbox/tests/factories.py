# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

"""factory_boy factories for lizard-blockbox"""

# Python 3 is coming
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


import factory

from lizard_blockbox import models

# Same order as in models


class ReachFactory(factory.Factory):
    class Meta:
        model = models.Reach

    slug = "SL"


class TrajectoryFactory(factory.Factory):
    class Meta:
        model = models.Trajectory

    name = "trajectorynaam"


class RiverSegmentFactory(factory.Factory):
    class Meta:
        model = models.RiverSegment

    location = 0.0
    reach = factory.SubFactory(ReachFactory)


class NamedReachFactory(factory.Factory):
    class Meta:
        model = models.NamedReach

    name = "Some named reach"


class SubsetReachFactory(factory.Factory):
    class Meta:
        model = models.SubsetReach

    reach = factory.SubFactory(ReachFactory)
    named_reach = factory.SubFactory(NamedReachFactory)
    km_from = 1
    km_to = 100


class MeasureFactory(factory.Factory):
    class Meta:
        model = models.Measure

    name = "Some measure"
    short_name = "mesur"
    measure_type = "o"
    km_from = 0
    km_to = 100
    reach = None
    riverpart = None
    mhw_profit_cm = None
    mhw_profit_m2 = None
    minimal_investment_costs = None
    investment_costs = None
    maximal_investment_costs = None


class WaterLevelDifferenceFactory(factory.Factory):
    class Meta:
        model = models.WaterLevelDifference

    riversegment = factory.SubFactory(RiverSegmentFactory)
    measure = factory.SubFactory(MeasureFactory)
    protection_level = "1250"
    level_difference = -1


class VertexFactory(factory.Factory):
    class Meta:
        model = models.Vertex

    name = "Some vertex"
    header = "Some header"


class VertexValueFactory(factory.Factory):
    class Meta:
        model = models.VertexValue

    vertex = factory.SubFactory(VertexFactory)
    riversegment = factory.SubFactory(RiverSegmentFactory)
    year = "2100"
    value = 1.0
