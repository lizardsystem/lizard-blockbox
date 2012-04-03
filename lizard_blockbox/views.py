# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from lizard_map.views import MapView


class BlockboxView(MapView):
    """Show reach including pointers to relevant data URLs."""
    template_name = 'lizard_blockbox/blockbox.html'
    edit_link = '/admin/lizard_blockbox/'
