# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lizard_blockbox.fields import EmptyStringFloatField


class Reach(models.Model):
    """A reach of a river.

    Dutch: *riviertak*.

    """
    slug = models.SlugField(
        blank=False,
        help_text=u"Slug.")

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = _('reach')
        verbose_name_plural = _('reaches')


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


class NamedReach(models.Model):
    """A named Reach, a collection of reaches.

    Dutch: *riviertak*.
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class SubsetReach(models.Model):
    """A subset Reach

    a definition of start, end kilometers and the Reach name.
    """

    reach = models.ForeignKey(Reach)
    named_reach = models.ForeignKey(NamedReach)
    km_from = models.IntegerField()
    km_to = models.IntegerField()


class CityLocation(models.Model):
    """River City locations."""

    reach = models.ForeignKey(Reach)
    city = models.CharField(max_length=100)
    km = models.IntegerField()

    def __unicode__(self):
        return u'city: {city}, km: {km}'.format(**self.__dict__)


class Measure(models.Model):
    """A Measure

    The name of the measure and the short name defined for reference
    with the spreadsheets.

    """

    name = models.CharField(
        'Titel',
        max_length=200,
        blank=True,
        null=True)
    short_name = models.CharField(
        'Code',
        max_length=100,
        blank=True,
        null=True)
    measure_type = models.CharField(
        'Type',
        max_length=100,
        blank=True,
        null=True)
    km_from = models.IntegerField(
        'Km van',
        null=True,
        blank=True)
    km_to = models.IntegerField(
        'Km tot',
        null=True,
        blank=True)

    reach = models.ForeignKey(
        Reach, blank=True, null=True, verbose_name=_('reach'))
    riverpart = models.CharField(
        'Rivierdeel', max_length=100, blank=True, null=True)
    mhw_profit_cm = EmptyStringFloatField(
        'MHW winst cm', blank=True, null=True)
    mhw_profit_m2 = EmptyStringFloatField(
        'MHW winst m2', blank=True, null=True)
    investment_costs = EmptyStringFloatField(
        'Kosten investering', blank=True, null=True)
    benefits = EmptyStringFloatField(
        'Baten', blank=True, null=True)
    b_o_costs = EmptyStringFloatField(
        'Kosten B&O', blank=True, null=True)
    reinvestment = EmptyStringFloatField(
        'Herinvestering', blank=True, null=True)
    damage = models.CharField(
        'Schade', max_length=100, blank=True, null=True)
    total_costs = EmptyStringFloatField(
        'Kosten totaal', blank=True, null=True)
    quality_of_environment = models.CharField(
        'Ruimtelijke kwaliteit',
        max_length=100, blank=True, null=True)

    exclude = models.ManyToManyField(
        'self',
        blank=True, null=True)

    def __unicode__(self):
        name = self.name or self.short_name
        return u'%s' % name

    def pretty(self):
        """Return list with verbose name + value for every field for the view.
        """
        ignore = ['id', 'name', 'exclude']
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

    per Riversegment and Measure.

    """
    riversegment = models.ForeignKey(RiverSegment)
    reference = models.FloatField()

    def __unicode__(self):
        return '%s Reference: %s' % (
            self.riversegment, self.flooding_chance)


class WaterLevelDifference(models.Model):
    """Water Level Difference

    per Riversegmentand Measure.

    Dutch: *peilverschil*.

    """

    riversegment = models.ForeignKey(RiverSegment)
    measure = models.ForeignKey(Measure)
    reference_value = models.ForeignKey(ReferenceValue)

    level_difference = models.FloatField()

    def __unicode__(self):
        return '%s %s Reference: %s Difference: %s' % (
            self.riversegment, self.measure, self.flooding_chance,
            self.level_difference)


class Vertex(models.Model):
    """Vertex

    Dutch: *hoekpunt*.
    """

    name = models.CharField(max_length=100)
    named_reaches = models.ManyToManyField(
        NamedReach, null=True, blank=True)


class VertexValue(models.Model):
    """Vertex Value for a specific location."""

    vertex = models.ForeignKey(Vertex)
    riversegment = models.ForeignKey(RiverSegment)
    value = models.FloatField()
