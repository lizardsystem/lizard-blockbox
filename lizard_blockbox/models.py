# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models

from lizard_shape import models as shape_models


class BlockboxShape(shape_models.Shape):
    """Abstract class for adding data to shapefiles.

    Abstract for now
    """
    data_file = models.FileField(upload_to=shape_models.UPLOAD_TO,
                                 blank=True)

    def save(self, *args, **kwargs):
        if self.data_file:
            data_base_name = self.date_file.name.rpartition('.')
            shp_base_name = self.shp_file.name.rpartition('.')
            if data_base_name != shp_base_name:
                raise shape_models.ShapeNameError(
                    "Uploaded files do not have common filename base.")
        return super(BlockboxShape, self).save(*args, **kwargs)

    class Meta:
        abstract = True
