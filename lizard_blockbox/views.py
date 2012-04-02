# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from lizard_map.views import MapView
from lizard_ui.views import UiView

from lizard_blockbox.models import Reach


class ReachChoiceView(UiView):
    """Show choice of river reaches (NL: *riviertakken*)."""
    template_name = "lizard_blockbox/reach_choice.html"
    reaches = Reach.objects.all()


class ReachView(MapView):
    """Show reach including pointers to relevant data URLs."""
    template_name = "lizard_blockbox/reach.html"



