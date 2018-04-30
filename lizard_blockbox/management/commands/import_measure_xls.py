import logging
import os
import re
import sys

from django.core.management.base import BaseCommand

from lizard_blockbox import import_helpers

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<directory> OR <excelfile excelfile ...>'
    help = ("Imports measure excelfiles, "
            "use --flush to flush the previous imports.")

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            dest='flush',
            default=False,
            help='Delete poll instead of closing it',
        )

    def handle(self, *args, **options):
        flush = options['flush']
        if flush:
            import_helpers.flush_database(self.stdout)

        if len(args) == 0:
            if not flush:
                print "Pass a directory as argument."
                sys.exit(1)
            sys.exit(0)

        if os.path.isdir(args[0]):
            excelpaths = latest_xls(args[0])
        else:
            excelpaths = args

        for excelpath in excelpaths:
            import_helpers.import_measure_xls(excelpath, self.stdout)


def latest_xls(d):
    """Return a list of the latest version of each measure xls in a directory.

    First, get all files like {name}_v{number}.xls. Then, for each {name}
    determine the latest {number}. Add the corresponding file to a list.

    For example, if a directory contains the following files:

    IVM_1250_v20141117.xls
    IVM_1250_v20141118.xls
    PKB_LT_Waal_v20141117.xls
    PKB_LT_Waal_v20141118.xls
    bar.xls
    foo.xls

    Then, only these are returned:

    IVM_1250_v20141118.xls
    PKB_LT_Waal_v20141118.xls

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
