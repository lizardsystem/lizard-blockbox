from django.db import models
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules


class EmptyStringFloatField(models.FloatField):
    empty_strings_allowed = True
    description = _("Floating point number: converts empty string to None")

    def get_prep_value(self, value):
        if isinstance(value, basestring) and value.strip() == '':
            return None
        return super(EmptyStringFloatField, self).get_prep_value(value)

# Add introspection rules for EmptyStringFloatField
add_introspection_rules([], ['lizard_blockbox.fields.EmptyStringFloatField'])
