# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Reach(models.Model):
    """A reach of a river.

    Dutch: *riviertak*.

    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        blank=False,
        help_text=u"Slug will be automatically generated from the name.")

    def __unicode__(self):
        return '%s' % self.name


class RiverSegment(gis_models.Model):
    """
    A RiverSegement

    """

    location = models.IntegerField()
    reach = models.ForeignKey(Reach)
    the_geom = gis_models.PointField(srid=4326, null=True, blank=True)
    objects = gis_models.GeoManager()

    def __unicode__(self):
        return '%i' % self.location


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

    name = models.CharField(
        _('name'),
        max_length=100,
        blank=True,
        null=True)
    short_name = models.CharField(
        _('short name'),
        max_length=100,
        blank=True,
        null=True)
    measure_type = models.CharField(
        _('measure type'),
        max_length=100,
        blank=True,
        null=True)
    traject = models.CharField(
        _('traject'),
        max_length=100,
        blank=True,
        null=True)
    km_from = models.IntegerField(
        _('from km'),
        null=True,
        blank=True)
    km_to = models.IntegerField(
        _('to km'),
        null=True,
        blank=True)

    def __unicode__(self):
        name = self.name or self.short_name
        return u'%s' % name

    def pretty(self):
        """Return list with verbose name + value for every field for the view.
        """
        ignore = ['id', 'name']
        result = []
        for field in self._meta.fields:
            if field.name in ignore:
                continue
            result.append({'label': field.verbose_name,
                           'name': field.name,
                           'value': getattr(self, field.name)})
        return result

    class Meta:
        permissions = (("can_view_blockbox", "Can view blockbox"),)
        # ^^^ Note: just a generic blockbox permission. Just needs to be on a
        # model, not specifically *this* model.
        ordering = ('km_from',)


class ReferenceValue(models.Model):
    """Reference Value for the water height

    per Riversegment, Measure and Flooding Chance.

    """
    riversegment = models.ForeignKey(RiverSegment)
    flooding_chance = models.ForeignKey(FloodingChance)
    reference = models.FloatField()
    target = models.FloatField()

    def __unicode__(self):
        return '%s Reference: %s' % (
            self.riversegment, self.flooding_chance)


class WaterLevelDifference(models.Model):
    """Water Level Difference

    per Riversegment, Measure and Flooding Chance.

    Dutch: *peilverschil*.

    """

    riversegment = models.ForeignKey(RiverSegment)
    measure = models.ForeignKey(Measure)
    flooding_chance = models.ForeignKey(FloodingChance)
    reference_value = models.ForeignKey(ReferenceValue)

    level_difference = models.FloatField()

    def __unicode__(self):
        return '%s %s Reference: %s Difference: %s' % (
            self.riversegment, self.measure, self.flooding_chance,
            self.level_difference)
