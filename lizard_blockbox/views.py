# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging
import operator
import os
from hashlib import md5
from collections import defaultdict

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from lizard_map.lizard_widgets import Legend
from lizard_map.views import MapView
from lizard_ui.layout import Action
from lizard_ui.models import ApplicationIcon
from lizard_ui.views import UiView

from lizard_blockbox import models
from lizard_blockbox.utils import namedreach2riversegments

SELECTED_MEASURES_KEY = 'selected_measures_key'

logger = logging.getLogger(__name__)


class BlockboxView(MapView):
    """Show reach including pointers to relevant data URLs."""
    template_name = 'lizard_blockbox/blockbox.html'
    edit_link = '/admin/lizard_blockbox/'
    require_application_icon_with_permission = True

    @property
    def content_actions(self):
        actions = super(BlockboxView, self).content_actions
        to_table_text = _('Show table')
        to_map_text = _('Show map')
        switch_map_and_table = Action(
            name=to_table_text,
            description=_('Switch between a graph+map view and a graph+table '
                          'view.'),
            icon='icon-random',
            url='#table',
            data_attributes={'to-table-text': to_table_text,
                             'to-map-text': to_map_text},
            klass='toggle_map_and_table')
        actions.insert(0, switch_map_and_table)
        return actions

    def reaches(self):
        reaches = models.NamedReach.objects.all().values('name')
        selected_river = _selected_river(self.request)
        for reach in reaches:
            if reach['name'] == selected_river:
                reach['selected'] = True
        return reaches

    def selected_measures(self):
        selected_measures = _selected_measures(self.request)
        return models.Measure.objects.filter(
            short_name__in=selected_measures).values(
            'name', 'short_name', 'measure_type', 'km_from')

    def measure_headers(self):
        """Return headers for measures table."""
        measure = models.Measure.objects.all()[0]
        return [field['label'] for field in measure.pretty()]

    def measures(self):
        measures = models.Measure.objects.all()
        selected_measures = _selected_measures(self.request)
        available_factsheets = _available_factsheets()
        # selected_river = _selected_river(self.request)
        result = []
        for measure_obj in measures:
            measure = {}
            measure['fields'] = measure_obj.pretty()
            measure['selected'] = measure_obj.short_name in selected_measures
            # measure['in_selected_river'] = (
            #     measure_obj.riverpart == selected_river)
            measure['name'] = unicode(measure_obj)
            measure['short_name'] = measure_obj.short_name
            if measure_obj.short_name in available_factsheets:
                measure['pdf_link'] = reverse(
                    'measure_factsheet',
                    kwargs={'measure': measure_obj.short_name})
            result.append(measure)
        return result

    @property
    def legends(self):
        result_graph_legend = FlotLegend(
            name="Effecten grafiek",
            div_id='measure_results_graph_legend')
        all_types = models.Measure.objects.all().values_list(
            'measure_type', flat=True)
        labels = []
        for measure_type in set(all_types):
            if measure_type is None:
                labels.append(['x', 'Onbekend'])
            else:
                labels.append([measure_type[0].lower(), measure_type])
        labels.sort()
        measures_legend = FlotLegend(
            name="Maatregelselectie grafiek",
            div_id='measures_legend',
            labels=labels)
        result = [result_graph_legend, measures_legend]
        result += super(BlockboxView, self).legends
        return result


class FlotLegend(Legend):
    """UI widget for a flot graph legend."""
    template_name = 'lizard_blockbox/flot_legend_item.html'
    div_id = None
    labels = {}  # Only used for label explanation of y axis measure kinds.


class SelectedMeasuresView(UiView):
    """Show info on the selected measures."""
    template_name = 'lizard_blockbox/selected_measures.html'
    # require_application_icon_with_permission = True
    page_title = "Geselecteerde blokkendoos maatregelen"

    def selected_names(self):
        """Return set of selected measures from session."""
        return _selected_measures(self.request)

    def measures_per_reach(self):
        """Return selected measures, sorted per reach."""
        reaches = defaultdict(list)
        measures = models.Measure.objects.filter(
            short_name__in=self.selected_names())
        for measure in measures:
            if measure.reach:
                reach_name = measure.reach.slug
            else:
                reach_name = 'unknown'
            reaches[reach_name].append(measure)
        result = []
        print models.Measure._meta.fields
        for name, measures in reaches.items():
            reach = {'name': name,
                     'amount': len(measures),
                     'measures': measures}
            result.append(reach)
        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    @property
    def to_bookmark_url(self):
        """Return URL with the selected measures stored in the URL."""
        short_names = sorted(list(self.selected_names()))
        selected = ','.join(short_names)
        url = reverse('lizard_blockbox.bookmarked_measures',
                kwargs={'selected': selected})
        return url

    @property
    def breadcrumbs(self):
        result = super(SelectedMeasuresView, self).breadcrumbs
        result.append(Action(name=self.page_title))
        return result


class BookmarkedMeasuresView(SelectedMeasuresView):
    """Show info on the measures as selected by the URL."""
    to_bookmark_url = None

    @property
    def page_title(self):
        return "Bewaarde blokkendoos maatregelen (%s stuks)" % (
            len(self.selected_names()))

    def selected_names(self):
        """Return set of selected measures from URL info.

        The last part of the url, extracted as 'selected', is a
        comma-separated string with shortnames.

        """
        comma_separated = self.kwargs['selected']
        short_names = comma_separated.split(',')
        return set(short_names)


def fetch_factsheet(request, measure):
    """Return download header for nginx to serve pdf file."""

    # ToDo: Better security model based on views...
    if not ApplicationIcon.objects.filter(url__startswith='/blokkendoos'):
        # ToDo: Change to 403 with templates
        raise Http404

    if not measure in _available_factsheets():
        # There is no factsheet for this measure
        raise Http404

    response = HttpResponse()
    response['X-Accel-Redirect'] = '/protected/%s.pdf' % measure
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % measure
    # content-type is set in nginx.
    response['Content-Type'] = ''
    return response


def _available_factsheets():
    """Return a list of the available factsheets."""

    cache_key = 'available_factsheets'
    factsheets = cache.get(cache_key)
    if factsheets:
        return factsheets

    factsheets = [i.rstrip('.pdf') for i in os.listdir(settings.FACTSHEETS_DIR)
                  if i.endswith('pdf')]
    cache.set(cache_key, factsheets, 60 * 60 * 12)
    return factsheets


def _water_levels(flooding_chance, selected_river, selected_measures,
                  selected_vertex):
    cache_key = (str(flooding_chance) + str(selected_river) +
                 str(selected_vertex.id) + ''.join(selected_measures))
    cache_key = md5(cache_key).hexdigest()
    water_levels = cache.get(cache_key)
    if not water_levels:
        logger.info("Cache miss for _water_levels")

        measures = models.Measure.objects.filter(
            short_name__in=selected_measures)

        riversegments = namedreach2riversegments(selected_river)

        water_levels = []
        for segment in riversegments:
            measures_level = segment.waterleveldifference_set.filter(
                measure__in=measures, flooding_chance=flooding_chance
                ).aggregate(ld=Sum('level_difference'))['ld'] or 0
            try:
                vertex_level = models.VertexValue.objects.get(
                    vertex=selected_vertex, riversegment=segment).value
            except models.VertexValue.DoesNotExist:
                vertex_level = 0

            reference_absolute = models.ReferenceValue.objects.get(
                riversegment=segment, flooding_chance=flooding_chance
                ).reference
            vertex_level_normalized = vertex_level - reference_absolute
            d = {'vertex_level': vertex_level_normalized,
                 'measures_level': vertex_level_normalized + measures_level,
                 'reference_target': 0,
                 'location': segment.location,
                 'location_reach': '%i_%s' % (segment.location,
                                              segment.reach.slug),
                 }
            # This next part can probably go.
            try:
                city = models.CityLocation.objects.get(
                    km=segment.location, reach=segment.reach)
            except models.CityLocation.DoesNotExist:
                pass
            else:
                d['city'] = city.city
            water_levels.append(d)
        cache.set(cache_key, water_levels, 5 * 60)
    return water_levels


def calculated_measures_json(request):
    """Calculate the result of the measures."""

    flooding_chance = models.FloodingChance.objects.get(name="T1250")
    selected_river = _selected_river(request)
    selected_measures = _selected_measures(request)
    selected_vertex = _selected_vertex(request)
    water_levels = _water_levels(flooding_chance,
                                 selected_river,
                                 selected_measures,
                                 selected_vertex)

    response = HttpResponse(mimetype='application/json')
    json.dump(water_levels, response)
    return response


def city_locations_json(request):
    """Return the city locations for the selected river."""

    selected_river = _selected_river(request)
    reach = models.NamedReach.objects.get(name=selected_river)
    subset_reaches = reach.subsetreach_set.all()
    segments_join = (models.CityLocation.objects.filter(
            reach=element.reach,
            km__range=(element.km_from, element.km_to))
                     for element in subset_reaches)

    # Join the querysets in segments_join into one.
    city_locations = reduce(operator.or_, segments_join)
    city_locations = city_locations.distinct().order_by('km')

    json_list = [[km, city] for km, city in
                 city_locations.values_list('km', 'city')]

    response = HttpResponse(mimetype='application/json')
    json.dump(json_list, response)
    return response


def vertex_json(request):
    selected_river = _selected_river(request)
    vertexes = models.Vertex.objects.filter(named_reaches__name=selected_river)
    to_json = dict(vertexes.values_list('id', 'name').order_by('name'))
    response = HttpResponse(mimetype='application/json')
    json.dump(to_json, response)
    return response


def select_vertex(request):
    """Select the vertex."""

    if not request.POST:
        return
    request.session['vertex'] = request.POST['vertex']
    return HttpResponse()


def _selected_vertex(request):
    """Return the selected vertex."""
    if not 'vertex' in request.session:
        selected_river = _selected_river(request)
        vertex = models.Vertex.objects.filter(
            named_reaches__name=selected_river).order_by('name')[0]
        request.session['vertex'] = vertex.id
        return vertex
    return models.Vertex.objects.get(id=request.session['vertex'])


def _selected_river(request):
    """Return the selected river"""
    available_reaches = models.NamedReach.objects.values_list(
        'name', flat=True).distinct().order_by('name')
    if not 'river' in request.session:
        request.session['river'] = available_reaches[0]
    if request.session['river'] not in available_reaches:
        logger.warn("Selected river %s doesn't exist anymore.",
                    request.session['river'])
        request.session['river'] = available_reaches[0]
    return request.session['river']


def _selected_measures(request):
    """Return selected measures."""

    if not SELECTED_MEASURES_KEY in request.session:
        request.session[SELECTED_MEASURES_KEY] = set()
    return request.session[SELECTED_MEASURES_KEY]


def _unselectable_measures(request):
    """Return measure IDs that are not selectable.

    Current implementation is a temporary hack. Just disallow the measure two
    IDs further down the line...

    """
    measures_shortnames = list(models.Measure.objects.all().values_list(
        'short_name', flat=True))
    unselectable = []
    for shortname in _selected_measures(request):
        index = measures_shortnames.index(shortname) + 2
        if index < len(measures_shortnames):
            unselectable.append(measures_shortnames[index])
    return unselectable


@never_cache
def toggle_measure(request):
    """Toggle a measure on or off."""
    if not request.POST:
        return
    measure_id = request.POST['measure_id']
    selected_measures = _selected_measures(request)
    # Fix for empty u'' that somehow showed up.
    available_shortnames = list(models.Measure.objects.all().values_list(
            'short_name', flat=True))
    to_remove = []
    for shortname in selected_measures:
        if shortname not in available_shortnames:
            to_remove.append(shortname)
            logger.warn(
                "Removed unavailable shortname %r from selected measures.",
                shortname)
    if to_remove:
        selected_measures = selected_measures - set(to_remove)
        request.session[SELECTED_MEASURES_KEY] = selected_measures

    unselectable_measures = _unselectable_measures(request)
    if measure_id in selected_measures:
        selected_measures.remove(measure_id)
    elif measure_id not in available_shortnames:
        logger.error("Non-existing shortname %r passed to toggle_measure",
                     measure_id)
    elif not measure_id in unselectable_measures:
        selected_measures.add(measure_id)
    request.session[SELECTED_MEASURES_KEY] = selected_measures
    return HttpResponse(json.dumps(list(selected_measures)))


def select_river(request):
    """Select a river."""
    if not request.POST:
        return
    request.session['river'] = request.POST['river_name']
    return HttpResponse()


@never_cache
def list_measures_json(request):
    """Return a list with all known measures for the second graph."""

    measures = models.Measure.objects.all().values(
        'name', 'short_name', 'measure_type', 'km_from')
    for measure in measures:
        if not measure['measure_type']:
            measure['measure_type'] = 'Onbekend'
    all_types = list(
            set(measure['measure_type'] for measure in measures))
    all_types[all_types.index('Onbekend')] = 'XOnbekend'
    all_types.sort()
    all_types.reverse()
    all_types[all_types.index('XOnbekend')] = 'Onbekend'
    single_characters = []
    for measure_type in all_types:
        if measure_type is 'Onbekend':
            single_characters.append('x')
        else:
            single_characters.append(measure_type[0].lower())
    selected_measures = _selected_measures(request)
    unselectable_measures = _unselectable_measures(request)
    for measure in measures:
        measure['selected'] = measure['short_name'] in selected_measures
        measure['selectable'] = (
            measure['short_name'] not in unselectable_measures)
        measure['type_index'] = all_types.index(measure['measure_type'])
        measure['type_indicator'] = single_characters[measure['type_index']]
    response = HttpResponse(mimetype='application/json')
    json.dump(list(measures), response)
    return response
