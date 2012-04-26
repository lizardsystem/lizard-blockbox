from django.db import transaction

from lizard_blockbox import models

from lizard_blockbox.management.commands import import_measure_xls


class Command(import_measure_xls.Command):
    """Import command for measures excel sheets from Rijn river."""

    @transaction.commit_on_success
    def parse_sheet(self, sheet):
        measure, created = models.Measure.objects.get_or_create(
            short_name=sheet.name)
        if not created:
            #print 'This measure already exists: %s' % sheet.name
            return
        #print 'New measure: %s' % sheet.name
        # Flooding chance is always T1250, except for some parts of the Maas.
        flooding_T1250, _ = models.FloodingChance.objects.get_or_create(
            name='T1250')
        for row_nr in xrange(1, sheet.nrows):
            location, _, _, reference, _, difference, reach_slug = \
                sheet.row_values(row_nr)
            if not location.is_integer():
                continue
            try:
                riversegment = models.RiverSegment.objects.get(
                    location=location, reach__slug=reach_slug)
            except:
                print 'This location does not exist: %i %s' % (
                    location, reach_slug)
                continue

            ref_val, _ = models.ReferenceValue.objects.get_or_create(
                riversegment=riversegment,
                flooding_chance=flooding_T1250,
                defaults={'reference': reference,
                          'target': reference - 0.1}
                )

            models.WaterLevelDifference.objects.create(
                riversegment=riversegment,
                measure=measure,
                flooding_chance=flooding_T1250,
                reference_value=ref_val,
                level_difference=difference,
                )
