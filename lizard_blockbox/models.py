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


class Trajectory(models.Model):
    """A trajectory reach name."""

    name = models.TextField(blank=False,
                            help_text=u"The name of the trajectory.")
    reach = models.ManyToManyField(Reach, null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.name


class RiverSegment(gis_models.Model):
    """
    A RiverSegement.

    """

    location = models.IntegerField()
    reach = models.ForeignKey(Reach)
    objects = gis_models.GeoManager()

    def __unicode__(self):
        return '%i (%s)' % (self.location, self.reach)


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

    def __unicode__(self):
        return 'Subset reach {reach} of {named}'.format(
            reach=self.reach.slug,
            named=self.named_reach.name)


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
    life_costs = EmptyStringFloatField(
        'Levensduur kosten (ME)', blank=True, null=True)
    total_costs = EmptyStringFloatField(
        'Projectkosten gehele lifecyle (ME)', blank=True, null=True)
    investment_m2 = models.CharField(
        'Investering/m2',
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

            value = getattr(self, field.name)
            if isinstance(value, float) and 'costs' in field.name:
                value = round(value, 2)

            result.append({'label': field.verbose_name,
                           'name': field.name,
                           'value': value})
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


class WaterLevelDifference(models.Model):
    """Water Level Difference

    per Riversegment and Measure.

    Dutch: *peilverschil*.

    """

    riversegment = models.ForeignKey(RiverSegment)
    measure = models.ForeignKey(Measure)
    reference_value = models.ForeignKey(ReferenceValue)
    protection_level = models.CharField(
        max_length=4,
        choices=(
            ("250", "1 / 250"),
            ("1250", "1 / 1250")),
        default="1250")

    level_difference = models.FloatField()

    def reference(self):
        # For the admin.
        return self.reference_value.reference


class Vertex(models.Model):
    """Vertex

    Dutch: *hoekpunt*.
    """

    header = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    named_reaches = models.ManyToManyField(
        NamedReach, null=True, blank=True)

    def named_reaches_string(self):
        # For the admin.
        return ', '.join(
            self.named_reaches.all().values_list('name', flat=True))

    def __unicode__(self):
        return self.name


class VertexValue(models.Model):
    """Vertex Value for a specific location."""

    vertex = models.ForeignKey(Vertex)
    riversegment = models.ForeignKey(RiverSegment)
    year = models.CharField(
        max_length=4,
        choices=(
            ('2050', '2050'),
            ('2100', '2100')),
        default='2100')
    value = models.FloatField()
