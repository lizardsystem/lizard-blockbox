import os

from django.core.management.base import BaseCommand
from django.conf import settings

from lizard_blockbox import import_helpers

DATA_DIR = os.path.join(settings.BUILDOUT_DIR, 'deltaportaal/data')


class Command(BaseCommand):
    args = ''
    help = ("Run a data import using fab.")

    def handle(self, *args, **kwargs):
        """Import the data for lizard_blockbox from the source."""

        import_helpers.parse_trajectory_classification_excelfile(
            os.path.join(
                DATA_DIR,
                'excelsheets/trajectindeling/Trajectindeling.xls'),
            self.stdout)

        import_helpers.import_city_names(
            os.path.join(
                DATA_DIR,
                'excelsheets/gidslocaties/Gidslocaties.xls'),
            self.stdout)

        import_helpers.import_vertex_xls(
            os.path.join(
                DATA_DIR,
              'excelsheets/waterstandsopgave/'
              'Verzamelsheet Wateropgave DPR_16_Blokkendoos_geenFiguren.xls'),
            self.stdout)
        import_helpers.link_vertices_with_namedreaches()

        maatregeldir = os.path.join(DATA_DIR, 'excelsheets/maatregelen')
        for maatregelxls in os.listdir(maatregeldir):
            if maatregelxls.lower().endswith(".xls"):
                import_helpers.import_measure_xls(
                    os.path.join(maatregeldir, maatregelxls),
                    self.stdout)

        import_helpers.import_measure_table_xls(
            os.path.join(
                DATA_DIR,
                'excelsheets/eigenschappen/tabel_met_eigenschappen.xls'),
            self.stdout)

        import_helpers.import_excluding_measures_xls(
            os.path.join(
                DATA_DIR,
                'excelsheets/elkaar uitsluitende maatregelen',
                'Maatregelen die elkaar uitsluiten.xls'),
            self.stdout)

        import_helpers.import_trajectory_names_xls(
            os.path.join(
                DATA_DIR,
                'excelsheets/trajectindeling/hoofdtrajecten.xls'),
            self.stdout)
