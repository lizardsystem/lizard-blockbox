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
    FACTORY_FOR = models.Reach

    slug = "SL"


class RiverSegmentFactory(factory.Factory):
    FACTORY_FOR = models.RiverSegment

    location = 0.0
    reach = factory.SubFactory(ReachFactory)


class MeasureFactory(factory.Factory):
    FACTORY_FOR = models.Measure

    name = "Some measure"
    short_name = "mesur"
    measure_type = "o"
    km_from = 0
    km_to = 100
    reach = None
    riverpart = None
    mhw_profit_cm = None
    mhw_profit_m2 = None
    investment_costs = None
    life_costs = None
    total_costs = None
    investment_m2 = None
