# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging
import os

from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from lizard_map.coordinates import transform_point
from lizard_map.views import MapView
from lizard_ui.layout import Action
from lizard_ui.models import ApplicationIcon

from lizard_blockbox import models

SELECTED_MEASURES_KEY = 'selected_measures_key'
REFERENCE_TARGET = -0.11

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
        reaches = models.Reach.objects.values('name').distinct(
            ).order_by('name')
        for reach in reaches:
            if reach['name'] == 'Maas':
                # TODO
                reach['selected'] = True
        return reaches

    def selected_measures(self):
        selected_measures = _selected_measures(self.request)
        return models.Measure.objects.filter(
            short_name__in=selected_measures).values(
            'name', 'short_name', 'measure_type', 'km_from')

    # TODO: copy/pasted from selected_measures()
    def measures(self):
        measures = models.Measure.objects.all().values(
            'name', 'short_name', 'measure_type', 'km_from')
        selected_measures = _selected_measures(self.request)
        available_factsheets = _available_factsheets()
        for measure in measures:
            measure['selected'] = measure['short_name'] in selected_measures
            if not measure['name']:
                measure['name'] = measure['short_name']
            if not measure['measure_type']:
                measure['measure_type'] = 'Onbekend'
            if not measure['km_from']:
                measure['km_from'] = 'Onbekend'
            measure['pdf'] = measure['short_name'] in available_factsheets
        return measures


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
    # ToDo: Configure nginx
    response['X-Accel-Redirect'] = '/protected/%s.pdf' % measure
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


def _water_levels(flooding_chance, selected_river, selected_measures):
    cache_key = (str(flooding_chance) + str(selected_river) +
                 ''.join(selected_measures))
    water_levels = cache.get(cache_key)
    if not water_levels:
        logger.info("Cache miss for _water_levels")
        reach = models.Reach.objects.filter(name=selected_river)
        riversegments = models.RiverSegment.objects.filter(
            reach__in=reach).order_by('location')

        measures = models.Measure.objects.filter(
            short_name__in=selected_measures)

        water_levels = []
        for segment in riversegments:
            measures_level = segment.waterleveldifference_set.filter(
                measure__in=measures, flooding_chance=flooding_chance
                ).aggregate(ld=Sum('level_difference'))['ld'] or 0
            d = {'measures_level': measures_level,
                 'reference_target': REFERENCE_TARGET,
                 'reference_value': 0,
                 'target_difference': measures_level - REFERENCE_TARGET,
                 'location': segment.location,
                 'location_reach': '%i_%s' % (segment.location,
                                              segment.reach.slug)
                 }
            water_levels.append(d)
        cache.set(cache_key, water_levels, 5 * 60)
    return water_levels


@never_cache
def calculated_measures_json(request):
    """Calculate the result of the measures."""
    flooding_chance = models.FloodingChance.objects.get(name="T1250")
    selected_river = _selected_river(request)
    selected_measures = _selected_measures(request)
    water_levels = _water_levels(flooding_chance,
                                 selected_river,
                                 selected_measures)

    response = HttpResponse(mimetype='application/json')
    json.dump(water_levels, response)
    return response


def _selected_river(request):
    """Return the selected river"""

    if not 'river' in request.session:
        request.session['river'] = 'Maas'
    return request.session['river']


def _selected_measures(request):
    """Return selected measures."""

    if not SELECTED_MEASURES_KEY in request.session:
        request.session[SELECTED_MEASURES_KEY] = set([])
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
    unselectable_measures = _unselectable_measures(request)
    if measure_id in selected_measures:
        selected_measures.remove(measure_id)
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
    all_types = sorted(list(
            set(measure['measure_type'] for measure in measures)))

    selected_measures = _selected_measures(request)
    unselectable_measures = _unselectable_measures(request)
    for measure in measures:
        measure['selected'] = measure['short_name'] in selected_measures
        measure['selectable'] = (
            measure['short_name'] not in unselectable_measures)
        measure['type_index'] = all_types.index(measure['measure_type'])
    response = HttpResponse(mimetype='application/json')
    json.dump(list(measures), response)
    return response


def river_json(request):
    """Return the maas kilometers shape in GeoJSON."""

    features_geometry = [
        {'type': "Feature",
         'properties': {'MODELKM': '%i_%s' % (segment.location,
                                              segment.reach.slug)},
         'geometry': json.loads(transform_point(segment.the_geom.x,
                                     segment.the_geom.y,
                                     from_proj='wgs84',
                                     to_proj='google').json)
         } for segment in models.RiverSegment.objects.all()]

    response = HttpResponse(mimetype='application/json')
    json.dump({'type': 'FeatureCollection',
               'features': features_geometry}, response)
    return response
