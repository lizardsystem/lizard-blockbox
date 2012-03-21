# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from lizard_map.views import MapView


class BlockboxHome(MapView):
    """
    Test homepage for blockbox.
    """

    template_name = "lizard_blockbox/homepage.html"
