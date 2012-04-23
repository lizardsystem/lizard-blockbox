# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
#from collections import defaultdict

from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from lizard_map.coordinates import transform_point
from lizard_map.views import MapView
from lizard_ui.layout import Action

from lizard_blockbox import models

SELECTED_MEASURES_KEY = 'selected_measures_key'
REFERENCE_TARGET = -0.10


class BlockboxView(MapView):
    """Show reach including pointers to relevant data URLs."""
    template_name = 'lizard_blockbox/blockbox.html'
    edit_link = '/admin/lizard_blockbox/'

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

    def selected_measures(self):
        measures = models.Measure.objects.all().values(
            'name', 'short_name', 'measure_type', 'km_from')
        selected_measures = _selected_measures(self.request)
        return [measure for measure in measures if measure['short_name']
                in selected_measures]

    # TODO: copy/pasted from selected_measures()
    def measures(self):
        measures = models.Measure.objects.all().values(
            'name', 'short_name', 'measure_type', 'km_from')
        selected_measures = _selected_measures(self.request)
        for measure in measures:
            selected = measure['short_name'] in selected_measures
            measure['selected'] = selected
            if not measure['name']:
                measure['name'] = measure['short_name']
            if not measure['measure_type']:
                measure['measure_type'] = 'Onbekend'
            if not measure['km_from']:
                measure['km_from'] = 'Onbekend'
        return measures


@never_cache
def reference_json(request):
    """Fetch the reference and target values for all rivers and JSON them.
    """

    #XXX: Refactor with function calculated_measures_json.
    flooding_chance = models.FloodingChance.objects.filter(name="T250")
    references = models.ReferenceValue.objects.filter(
        flooding_chance=flooding_chance).values(
        'riversegment__location', 'reference', 'target')
    references = list(references)
    references.sort(key=lambda x: x['riversegment__location'])
    response = HttpResponse(mimetype='application/json')
    json.dump([{'reference_value': 0,
                'location': i['riversegment__location'],
                'reference_target': REFERENCE_TARGET,
                'measures_level': 0}
               for i in references],
              response)
    return response


@never_cache
def calculated_measures_json(request):
    """Fetch measure data and JSON it for a preliminary frontpage graph.
    """
    #XXX Refactor when needed.
    selected_measures = _selected_measures(request)
    if not selected_measures:
        return reference_json(request)
    measures = models.Measure.objects.filter(short_name__in=selected_measures)

    flooding_chance = models.FloodingChance.objects.filter(name="T250")

    water_level_diferences = models.WaterLevelDifference.objects.filter(
        measure__in=measures, flooding_chance=flooding_chance).values(
        'riversegment__location', 'level_difference',
        'reference_value__reference', 'reference_value__target')

    water_levels = {}
    for diff in water_level_diferences:
        #XXX: Refactor to use Default dict
        location = diff['riversegment__location']
        d = water_levels.get(location)
        if d is None:
            d = {'reference_value': 0,
                 # -0.10 chosen to have some target..
                 'reference_target': REFERENCE_TARGET,
                 'difference_level': diff['level_difference']}
        else:
            d['difference_level'] += diff['level_difference']
        water_levels[location] = d

    response = HttpResponse(mimetype='application/json')

    for key, value in water_levels.iteritems():
        value['location'] = key
        value['measures_level'] = value['difference_level']

    # Put it in a list because can't figure out how to
    # parse it correctly in coffeescript
    json.dump([i for i in water_levels.itervalues()], response)
    return response


def _selected_measures(request):
    """Return selected measures."""
    if not SELECTED_MEASURES_KEY in request.session:
        request.session[SELECTED_MEASURES_KEY] = set([])
    return request.session[SELECTED_MEASURES_KEY]


def toggle_measure(request):
    """Toggle a measure on or off."""
    if not request.POST:
        return
    measure_id = request.POST['measure_id']
    selected_measures = _selected_measures(request)
    if measure_id in selected_measures:
        selected_measures.remove(measure_id)
    else:
        selected_measures.add(measure_id)
    request.session[SELECTED_MEASURES_KEY] = selected_measures
    return HttpResponse(json.dumps(list(selected_measures)))


def list_measures_json(request):
    """Return a list with all known measures."""

    measures = models.Measure.objects.all().values(
        'name', 'short_name', 'measure_type', 'km_from')
    all_types = sorted(list(
            set(measure['measure_type'] for measure in measures)))

    selected_measures = _selected_measures(request)
    for measure in measures:
        selected = measure['short_name'] in selected_measures
        measure['selected'] = selected
        measure['type_index'] = all_types.index(measure['measure_type'])
    response = HttpResponse(mimetype='application/json')
    json.dump(list(measures), response)
    return response


def maas_river_json(request):
    """Return the maas kilometers shape in GeoJSON."""

    features_geometry = [
        {'type': "Feature",
         'properties': {'MODELKM': segment.location},
         'geometry': json.loads(transform_point(segment.the_geom.x,
                                     segment.the_geom.y,
                                     from_proj='wgs84',
                                     to_proj='google').json)
         } for segment in models.RiverSegment.objects.all()]

    response = HttpResponse(mimetype='application/json')
    json.dump({'type': 'FeatureCollection',
               'features': features_geometry}, response)
    return response
