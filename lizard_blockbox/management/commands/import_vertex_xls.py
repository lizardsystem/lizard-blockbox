from django.core.management.base import BaseCommand
from lizard_blockbox import import_helpers

import sys


class Command(BaseCommand):
    help = (
        "Imports the vertex excelfile, "
        "To flush use the management command: import_measure_xls --flush"
    )

    def add_arguments(self, parser):
        parser.add_argument("excelfile", nargs="+")

    def handle(self, *args, **options):
        if not options.get("excelfile", None):
            print("Pass excel files as arguments.")
            sys.exit(1)

        for excelpath in options["excelfile"]:
            import_helpers.import_vertex_xls(excelpath, self.stdout)

        import_helpers.link_vertices_with_namedreaches()
