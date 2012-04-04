# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.http import HttpResponse
from django.utils import simplejson as json
from lizard_map.views import MapView

from lizard_blockbox import models


class BlockboxView(MapView):
    """Show reach including pointers to relevant data URLs."""
    template_name = 'lizard_blockbox/blockbox.html'
    edit_link = '/admin/lizard_blockbox/'


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
    """Fetch dummy measure data and JSON it for a prelimnary frontpage graph.
    """

    flooding_chance = models.FloodingChance.objects.filter(name="T250")
    measure = models.Measure.objects.get(short_name='maatregel13')
    wld = models.WaterLevelDifference.objects.filter(
        measure=measure, flooding_chance=flooding_chance).values(
        'riversegment__location', 'level_difference',
        'reference_value__reference', 'reference_value__target')

    response = HttpResponse(mimetype='application/json')

    json.dump([{'riversegement': i['riversegment__location'],
                'difference_reference': i['level_difference'],
                'difference_target': ((i['level_difference'] +
                                      i['reference_value__reference']) -
                                      i['reference_value__target']),
                'absolute': (i['level_difference'] +
                             i['reference_value__reference'])}
               for i in wld],
              response)

    return response


def list_measures_json(request):
    """Return a list with all known measures."""

    measures = models.Measures.objects.all().values('name', 'short_name')
    response = HttpResponse(mimetype='application/json')
    json.dump([i for i in measures], response)
    return response
