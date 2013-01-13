import csv
import StringIO


class BaseFormatter(object):
    def start_format(self):
        return ''


    def format_record(self, record):
        pass


    def end_format(self):
        return ''


class CSVFormatter(BaseFormatter):
    def __init__(self, nvalues):
        self._nvalues = nvalues


    def format_values(self, strings):
        if len(strings) != self._nvalues:
            raise ValueError("The number of values to be formatted doesn't match the number of parsed values")

        return self._format_line(strings)


    def _format_line(self, values):
        out = StringIO.StringIO()

        writer = csv.writer(out)

        writer.writerow(map(lambda v: v.encode('utf-8'), values))

        line = out.getvalue()

        out.close()

        return line


    def __str__(self):
        return 'CSVFormatter(%s)' % (self._nvalues,)


    __repr__ = __str__
