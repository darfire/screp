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
    def __init__(self, nvalues, header=None):
        self._nvalues = nvalues

        if header is not None:
            self._hvalues = self._read_line(header)
            if len(self._hvalues) != nvalues:
                raise ValueError("CSV formatter: number of header columns (%s) differs from number of data columns (%s)"\
                        % (len(self._hvalues), nvalues))
        else:
            self._hvalues = None


    def start_format(self):
        if self._hvalues is not None:
            return self._format_line(self._hvalues)
        else:
            return ''


    def format_record(self, strings):
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


    def _read_line(self, line):
        io = StringIO.StringIO(line)

        return csv.reader(io).next()


    def __str__(self):
        return 'CSVFormatter(%s)' % (self._nvalues,)


    __repr__ = __str__
