# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lizard_blockbox.fields import EmptyStringFloatField
from lizard_blockbox.fields import EmptyStringUnknownFloatField


class Reach(models.Model):
    """A reach of a river.

    Dutch: *riviertak*.

    """
    slug = models.SlugField(
        blank=False,
        help_text=u"Slug.")

    # The number is needed to reconstruct the order in which the reaches
    # occur in the hoofdtrajecten.xls file
    number = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.slug

    class Meta:
        ordering = ('number',)
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

    @property
    def protection_levels(self):
        """Return list of protection levels that are present in in
        waterleveldifference for measures in this namedreach's
        reaches."""

        # Note: we know that all measure include the protection level
        # "1250".  So if we find one case that includes the other one,
        # "250", we know what to return.

        # I can't do this in one query, sorry.
        for subsetreach in self.subsetreach_set.all():
            if (WaterLevelDifference.objects.filter(
                protection_level="250",
                riversegment__reach__subsetreach=subsetreach,
                riversegment__location__lte=subsetreach.km_to,
                riversegment__location__gte=subsetreach.km_from).exists()):
                return ["250", "1250"]

        return ["1250"]

    def expanded_reaches(self):
        """Return a list of reaches created by taking the reaches of
        this namedreach, expanded so it is a trajectory. We take the
        first reach, see if it is in some Trajectory, and if there are
        reaches before it in that trajectory, we prepend them. Then we
        do the same for the end reach."""
        reaches = [
            subsetreach.reach
            for subsetreach in
            self.subsetreach_set.all().order_by('km_from')]

        if not reaches:
            return []

        # Prefix
        # Each reach is in 1 trajectory
        trajectory = reaches[0].trajectory_set.get()
        trajectory_reaches = list(trajectory.reach.all())  # Ordered by number
        location = trajectory_reaches.index(reaches[0])
        reaches = trajectory_reaches[:location] + reaches

        # Postfix
        trajectory = reaches[-1].trajectory_set.get()
        trajectory_reaches = list(trajectory.reach.all())  # Ordered by number
        location = trajectory_reaches.index(reaches[-1])
        reaches = reaches + trajectory_reaches[location + 1:]

        return reaches


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
    minimal_investment_costs = EmptyStringUnknownFloatField(
        'Minimale investeringskosten (ME)', blank=True, null=True)
    investment_costs = EmptyStringUnknownFloatField(
        'Investeringskosten (ME)', blank=True, null=True)
    maximal_investment_costs = EmptyStringUnknownFloatField(
        'Maximale investeringskosten (ME)', blank=True, null=True)

    efficiency = models.CharField(
        'Kosteneffectiviteit (m2 MHW verruiming/M euro)', max_length=255, blank=True, null=True)
    natuur = models.CharField(
        'Natuur (ha)', max_length=255, blank=True, null=True)
    grondverzet = models.CharField(
        'Grondverzet m3', max_length=255, blank=True, null=True)

    exclude = models.ManyToManyField(
        'self',
        blank=True, null=True)

    include = models.ManyToManyField(
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
            if isinstance(value, float) and (
                'costs' in field.name) or ('profit' in field.name):
                value = round(value, 1)

            result.append({'label': field.verbose_name,
                           'name': field.name,
                           'value': value})
        return result

    class Meta:
        permissions = (("can_view_blockbox", "Can view blockbox"),)
        # ^^^ Note: just a generic blockbox permission. Just needs to be on a
        # model, not specifically *this* model.
        ordering = ('km_from',)


class WaterLevelDifference(models.Model):
    """Water Level Difference

    per Riversegment and Measure.

    Dutch: *peilverschil*.

    """

    riversegment = models.ForeignKey(RiverSegment)
    measure = models.ForeignKey(Measure)

    protection_level = models.CharField(
        max_length=4,
        choices=(
            ("250", "1 / 250"),
            ("1250", "1 / 1250")),
        default="1250")

    level_difference = models.FloatField()


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

    @property
    def years(self):
        """Return sorted list of years that are present in this
        vertex' values."""
        return list(sorted(value['year'] for value in
                self.vertexvalue_set.values('year').distinct()))

    def __unicode__(self):
        return self.name


class VertexValue(models.Model):
    """Vertex Value for a specific location."""
    YEARS = frozenset(["2050", "2100"])

    vertex = models.ForeignKey(Vertex)
    riversegment = models.ForeignKey(RiverSegment)
    year = models.CharField(
        max_length=4,
        choices=(
            ('2050', '2050'),
            ('2100', '2100')),
        default='2100')
    value = models.FloatField()
