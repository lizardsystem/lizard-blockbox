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
    flooding_chance = models.FloodingChance.objects.filter(name="T250")
    qs = models.ReferenceValue.objects.filter(
        flooding_chance=flooding_chance).values(
        'riversegment__location', 'reference', 'target')

    response = HttpResponse(mimetype='application/json')
    json.dump([{'reference': float(i['reference']),
                        'riversegment': i['riversegment__location'],
                        'target': float(i['target'])} for i in qs],
              response)
    return response
