import logging
import os
import sys

from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ("Imports measure excelfiles, "
            "use --flush to flush the previous imports.")

    def add_arguments(self, parser):
        parser.add_argument('directory_or_excelfile', nargs='+')

        parser.add_argument(
            '--flush',
            action='store_true',
            dest='flush',
            default=False,
            help='Flush all blockbox models for a clean import',
        )

    def handle(self, *args, **options):
        flush = options['flush']
        if flush:
            import_helpers.flush_database(self.stdout)

        args = options.get('directory_or_excelfile', [])
        if len(args) == 0:
            if not flush:
                print("Pass a directory as argument.")
                sys.exit(1)
            sys.exit(0)

        if os.path.isdir(args[0]):
            excelpaths = list_xls(args[0])
        else:
            excelpaths = args

        for excelpath in excelpaths:
            import_helpers.import_measure_xls(excelpath, self.stdout)


def list_xls(d):
    """ Return a list of all xls files in a directory """
    if not os.path.isdir(d):
        return []
    return [f for f in os.listdir(d) if os.path.splitext(f)[-1] in ('.xls', '.xlsx')]
