# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models as gis_models
from django.db import models


class Reach(models.Model):
    """A reach of a river.

    Dutch: *riviertak*.

    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        blank=False,
        help_text=u"Slug will be automatically generated from the name.")


class RiverSegment(gis_models.Model):
    """
    A RiverSegement

    """

    location = models.IntegerField()
    the_geom = gis_models.PointField(srid='4326', null=True, blank=True)
    objects = gis_models.GeoManager()

    def __unicode__(self):
        return '%i' % self.location


class Scenario(models.Model):
    """
    A Scenario for the BlockBox.

    """

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % self.name


class Year(models.Model):
    """A year for the blockbox

    Corresponding values are calculated with respect to this year.

    """

    year = models.IntegerField()

    def __unicode__(self):
        return u'%i' % self.year


class FloodingChance(models.Model):
    """The FloodingChance

    """

    name = models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s' % self.name


class Measure(models.Model):
    """A Measure

    The name of the measure and the short name defined for reference
    with the spreadsheets.

    """

    name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        name = self.name or self.short_name
        return u'%s' % name

    class Meta:
        permissions = (("can_view_blockbox", "Can view blockbox"),)
        # ^^^ Note: just a generic blockbox permission. Just needs to be on a
        # model, not specifically *this* model.


class ReferenceValue(models.Model):
    """Reference Value for the water height

    per Riversegment, Measure, Scenario, Year and Flooding Chance.

    """
    riversegment = models.ForeignKey(RiverSegment)
    scenario = models.ForeignKey(Scenario)
    year = models.ForeignKey(Year)
    flooding_chance = models.ForeignKey(FloodingChance)

    reference = models.FloatField()
    target = models.FloatField()

    # class Meta:
    #     unique_together = ('riversegment', 'scenario', 'year',
    #                        'flooding_chance')

    def __unicode__(self):
        return '%s %s %s Reference: %s' % (
            self.riversegment, self.scenario,
            self.year, self.flooding_chance)


class WaterLevelDifference(models.Model):
    """Water Level Difference

    per Riversegment, Measure, Scenario, Year and Flooding Chance.

    Dutch: *peilverschil*.

    """

    riversegment = models.ForeignKey(RiverSegment)
    measure = models.ForeignKey(Measure)
    scenario = models.ForeignKey(Scenario)
    year = models.ForeignKey(Year)
    flooding_chance = models.ForeignKey(FloodingChance)
    reference_value = models.ForeignKey(ReferenceValue)

    level_difference = models.FloatField()

    def __unicode__(self):
        return '%s %s %s %s Reference: %s Delta: %s' % (
            self.riversegment, self.measure, self.scenario,
            self.year, self.flooding_chance, self.level_difference)
