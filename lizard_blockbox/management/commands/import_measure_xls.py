from optparse import make_option
import logging
import os
import re
import sys

from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<directory>'
    help = ("Imports measure excelfiles, "
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
                print "Pass a directory as argument."
                sys.exit(1)
            sys.exit(0)

        d = args[0]  # directory

        if not os.path.isdir(d):
            print "Pass a directory as argument."
            sys.exit(1)

        for excelpath in self.latest(d):
            import_helpers.import_measure_xls(excelpath, self.stdout)

    def latest(self, d):
        """Return a list of the latest version of each file in a directory.

        First, get all files like {name}_v{number}.xls. Then, for each {name}
        determine the latest {number}. Add the corresponding file to a list.

        """
        files = [f for f in os.listdir(d) if re.match(r'.+_v\d+\.xls', f)]
        names = set([f.rsplit('_v', 1)[0] for f in files])
        files = []
        for name in names:
            f = sorted([
                f for f in os.listdir(d)
                if re.match(name + r'_v\d+\.xls', f)
            ])[-1]
            files.append(os.path.join(d, f))
        return files
