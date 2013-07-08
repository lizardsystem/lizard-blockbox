import os

from django.core.management.base import BaseCommand
from django.conf import settings

from lizard_blockbox import import_helpers

DATA_DIR = os.path.join(settings.BUILDOUT_DIR, 'deltaportaal/data')

COMMANDS = """
bin/django import_trajectory_classification_xls {DATA_DIR}/excelsheets/trajectindeling/Trajectindeling.xls
bin/django import_city_names {DATA_DIR}/excelsheets/gidslocaties/Gidslocaties.xls
bin/django import_vertex_xls '{DATA_DIR}/excelsheets/waterstandsopgave/Verzamelsheet Wateropgave DPR_16_Blokkendoos_geenFiguren.xls'
bin/django import_measure_xls {DATA_DIR}/excelsheets/maatregelen/*.xls
bin/django import_measure_table_xls {DATA_DIR}/excelsheets/eigenschappen/tabel_met_eigenschappen.xls
bin/django import_excluding_measures '{DATA_DIR}/excelsheets/elkaar uitsluitende maatregelen/Maatregelen die elkaar uitsluiten.xls'
bin/django import_trajectory_names_xls {DATA_DIR}/excelsheets/trajectindeling/hoofdtrajecten.xls
""".format(DATA_DIR=DATA_DIR)


class Command(BaseCommand):
    args = ''
    help = ("Run a data import using fab.")

    def handle(self, *args, **kwargs):
        """Import the data for lizard_blockbox from the source."""

        output = import_helpers.run_commands_in(
            settings.BUILDOUT_DIR, COMMANDS, shell=True)

        self.stdout.write(output)
