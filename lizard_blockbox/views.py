# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
#from collections import defaultdict

from django.http import HttpResponse
from django.utils import simplejson as json
from lizard_map.views import MapView
from lizard_ui.layout import Action
from django.utils.translation import ugettext as _

from lizard_blockbox import models
from lizard_map.coordinates import transform_point

SELECTED_MEASURES_KEY = 'selected_measures_key'


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


def reference_json(request):
    """Fetch the reference and target values for all rivers and JSON them.
    """

    flooding_chance = models.FloodingChance.objects.filter(name="T250")
    references = models.ReferenceValue.objects.filter(
        flooding_chance=flooding_chance).values(
        'riversegment__location', 'reference', 'target')

    response = HttpResponse(mimetype='application/json')
    json.dump([{'reference': float(i['reference']),
                'riversegment': i['riversegment__location'],
                'target': float(i['target'])} for i in references],
              response)
    return response


def calculated_measures_json(request):
    """Fetch dummy measure data and JSON it for a preliminary frontpage graph.
    """

    flooding_chance = models.FloodingChance.objects.filter(name="T250")
    selected_measures = _selected_measures(request)
    measures = models.Measure.objects.filter(short_name__in=selected_measures)
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
            d = {'reference_value': diff['reference_value__reference'],
                 'reference_target': diff['reference_value__target'],
                 'difference_level': diff['level_difference']}
        else:
            d['difference_level'] += diff['level_difference']
        water_levels[location] = d

    response = HttpResponse(mimetype='application/json')

    for value in water_levels.itervalues():
        absolute = value['reference_value'] + value['difference_level']
        value['measures_level'] = absolute
        value['difference_to_reference'] = absolute - value['reference_value']
        value['difference_to_target'] = absolute - value['reference_target']

    json.dump(water_levels, response)

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

    measures = models.Measure.objects.all().values('name', 'short_name')
    selected_measures = _selected_measures(request)
    for measure in measures:
        selected = measure['short_name'] in selected_measures
        measure['selected'] = selected
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
