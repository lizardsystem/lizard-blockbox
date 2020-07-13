from functools import reduce
from lizard_blockbox import models

import operator


def namedreach2riversegments(river):
    reach = models.NamedReach.objects.get(name=river)
    subset_reaches = reach.subsetreach_set.all()

    segments_join = (
        models.RiverSegment.objects.filter(
            reach=element.reach, location__range=(element.km_from, element.km_to)
        )
        for element in subset_reaches
    )

    # Join the querysets in segments_join into one.
    riversegments = reduce(operator.or_, segments_join)
    return riversegments.distinct().order_by("location")


def namedreach2measures(river):
    reach = models.NamedReach.objects.get(name=river)
    subset_reaches = reach.subsetreach_set.all()

    segments_join = (
        models.Measure.objects.filter(
            reach=element.reach, km_from__range=(element.km_from, element.km_to)
        )
        for element in subset_reaches
    )

    # Join the querysets in segments_join into one.
    measures = reduce(operator.or_, segments_join)
    return measures.distinct().order_by("km_from").values_list("short_name", flat=True)
