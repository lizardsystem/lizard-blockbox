# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models


class Reach(models.Model):
    """A reach of a river.

    Dutch: *riviertak*.

    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        blank=False,
        help_text=u"Slug will be automatically generated from the name.")


class RiverSegment(models.Model):
    #branch = models.CharField(max_length=100)
    location = models.IntegerField()

    def __unicode__(self):
        return '%i' % self.location


class Scenario(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % self.name


class Year(models.Model):
    year = models.IntegerField()

    def __unicode__(self):
        return u'%i' % self.year


class FloodingChance(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s' % self.name


class Measure(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        name = self.name or self.short_name
        return u'%s' % name

    class Meta:
        permissions = (("can_view_blockbox", "Can view blockbox"),)
        # ^^^ Note: just a generic blockbox permission. Just needs to be on a
        # model, not specifically *this* model.


class Delta(models.Model):
    riversegment = models.ForeignKey(RiverSegment)
    measure = models.ForeignKey(Measure)
    scenario = models.ForeignKey(Scenario)
    year = models.ForeignKey(Year)
    flooding_chance = models.ForeignKey(FloodingChance)

    delta = models.DecimalField(max_digits=6, decimal_places=4)

    def __unicode__(self):
        return '%s %s %s %s Reference: %s Delta: %s' % (
            self.riversegment, self.measure, self.scenario,
            self.year, self.flooding_chance, self.delta)


class ReferenceValue(models.Model):
    riversegment = models.ForeignKey(RiverSegment)
    scenario = models.ForeignKey(Scenario)
    year = models.ForeignKey(Year)
    flooding_chance = models.ForeignKey(FloodingChance)

    reference = models.DecimalField(max_digits=6, decimal_places=4)
    target = models.DecimalField(max_digits=6, decimal_places=4)

    def __unicode__(self):
        return '%s %s %s Reference: %s' % (
            self.riversegment, self.scenario,
            self.year, self.flooding_chance)
