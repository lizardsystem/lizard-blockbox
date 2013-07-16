from optparse import make_option
import logging
import sys

from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<excelfile excelfile ...>'
    help = ("Imports the measure excelfile, "
            "use --flush to flush the previous imports.")

    option_list = BaseCommand.option_list + (
        make_option('--flush',
                    action='store_true',
                    dest='flush',
                    default=False,
                    help='Flush all blockbox models for a clean import'),)

    def handle(self, *args, **options):
        flush = options['flush']
        if flush:
            import_helpers.flush_database(self.stdout)

        if len(args) == 0:
            if not flush:
                print "Pass excel files as arguments."
                sys.exit(1)
            sys.exit(0)

        for excelpath in args:
            import_helpers.import_measure_xls(excelpath, self.stdout)
