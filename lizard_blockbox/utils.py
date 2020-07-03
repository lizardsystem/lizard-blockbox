import operator
import csv
import codecs
from functools import reduce
from io import StringIO

from lizard_blockbox import models


def namedreach2riversegments(river):
    reach = models.NamedReach.objects.get(name=river)
    subset_reaches = reach.subsetreach_set.all()

    segments_join = (
        models.RiverSegment.objects.filter(
            reach=element.reach,
            location__range=(element.km_from, element.km_to))
        for element in subset_reaches)

        # Join the querysets in segments_join into one.
    riversegments = reduce(operator.or_, segments_join)
    return riversegments.distinct().order_by('location')


def namedreach2measures(river):
    reach = models.NamedReach.objects.get(name=river)
    subset_reaches = reach.subsetreach_set.all()

    segments_join = (
        models.Measure.objects.filter(
            reach=element.reach,
            km_from__range=(element.km_from, element.km_to))
        for element in subset_reaches)

    # Join the querysets in segments_join into one.
    measures = reduce(operator.or_, segments_join)
    return measures.distinct().order_by('km_from').values_list('short_name',
                                                               flat=True)

# Taken from http://docs.python.org/2/library/csv.html
# Fixes writes/reads for unicode.


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [str(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        unicode_row = (str(s) for s in row)
        self.writer.writerow([s.encode("utf-8") for s in unicode_row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
