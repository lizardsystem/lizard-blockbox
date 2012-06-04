import operator

from lizard_blockbox import models


def namedreach2riversegments(river):
    reach = models.NamedReach.objects.get(name=river)
    subset_reaches = reach.subsetreach_set.all()

    segments_join = (models.RiverSegment.objects.filter(
            reach=element.reach,
            location__range=(element.km_from, element.km_to))
                     for element in subset_reaches)

        # Join the querysets in segments_join into one.
    riversegments = reduce(operator.or_, segments_join)
    return riversegments.distinct().order_by('location')


