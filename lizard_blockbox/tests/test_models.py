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
