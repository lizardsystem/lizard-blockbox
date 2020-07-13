"""Lizard Widgets"""

from django.template import Context
from django.template import loader
from django.utils.safestring import mark_safe


class Legend(object):
    """Wrapper/interface for legends.

    This is used for documentation, to define an interface and to generate
    the html.

    To change the html used to render a workspace acceptable, redefine
    ``template`` or lizard_map/workspace_acceptable.html.

    - **name**: name of the legend.

    - **image_url**: url of the legend image.


    """

    template_name = "lizard_map/legend_item.html"
    name = None
    subitems = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError("Argument %s cannot be set." % key)

    def to_html(self):
        template = loader.get_template(self.template_name)
        return mark_safe(template.render(dict(legend=self)))
