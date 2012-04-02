# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from lizard_map.views import MapView
from lizard_ui.views import UiView

from lizard_blockbox.models import Reach


class BlockboxHome(MapView):
    """
    Test homepage for blockbox.
    """

    template_name = "lizard_blockbox/homepage.html"


class RiverChoiceView(UiView):
    """Show choice of rivers."""
    reaches = Reach.objects.all()
