from django.db import models
from django.utils.translation import ugettext_lazy as _


class EmptyStringFloatField(models.FloatField):
    empty_strings_allowed = True
    description = _("Floating point number: converts empty string to None")

    def get_prep_value(self, value):
        if isinstance(value, basestring) and value.strip() == '':
            return None
        return super(EmptyStringFloatField, self).get_prep_value(value)


class EmptyStringUnknownFloatField(models.FloatField):
    empty_strings_allowed = True
    description = _(
        "Floating point number: converts empty strging and the "
        "string 'Onbekend' to None")

    def get_prep_value(self, value):
        if (isinstance(value, basestring) and
            value.strip().lower() in ('', 'onbekend')):
            return None

        return super(EmptyStringUnknownFloatField, self).get_prep_value(value)
