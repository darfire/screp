import sys
from optparse import OptionParser
import lxml.etree as etree
import lxml.html as html
from lxml.cssselect import CSSSelector
import urllib2
import urlparse

from .format_parsers import (
        parse_csv_formatter,
        parse_anchor,
        )
from .context import (
        XMLContext,
        )
from .utils import raise_again

class BaseDataSource(object):
    name = 'Unknown'

    def read_data(self):
        pass


class OpenedFileDataSource(object):
    def __init__(self, name, ofile):
        self._file = ofile
        self.name = name


    def read_data(self):
        return self._file.read()


class URLDataSource(object):
    def __init__(self, url):
        self._url = url
        self.name = url
        

    def read_data(self):
        return urllib2.urlopen(self._url).read()


class FileDataSource(object):
    def __init__(self, fname):
        self._fname = fname
        self.name = fname


    def read_data(self):
        with open(self._fname, 'r') as f:
            return f.read()


def report_error(e):
    print >>sys.stderr, "ERROR: %s" % (e,)


def print_record(string):
    sys.stdout.write(string)


def get_formatter():
    try:
        if options.csv is not None:
            return parse_csv_formatter(options.csv, header=options.csv_header)

        raise ValueError('No format defined!')
    except Exception as e:
        raise_again('Parsing format specification: %s' % (e,))


def get_selector(selector):
    try:
        return CSSSelector(selector)
    except Exception as e:
        raise_again('Parsing selector: %s' % (e,))


def get_anchor(string):
    try:
        return parse_anchor(string)
    except Exception as e:
        raise_again('Parsing anchor: %s' % (e,))


def parse_xml_data(data):
    try:
        parser = etree.HTMLParser()

        return etree.fromstring(data, parser)
    except Exception as e:
        raise_again('Parsing document: %s' % (e,))


def compute_value(substitor, context):
    try:
        return substitor.execute(context)
    except Exception as e:
        if options.stop_on_error:
            raise
        else:
            return options.null_value


def compute_anchor(anchor, context):
    try:
        return anchor.execute(context)
    except Exception as e:
        if options.stop_on_error:
            raise


def get_context(root, element, anchors):
    context = XMLContext(element, root)
    for a in anchors:
        v = compute_anchor(a, context)
        if v is not None:
            context.add_anchor(a.name, v)

    return context


def screp_source(formatter, terms, anchors, selector, source):
    try:
        data = source.read_data()
        dom = parse_xml_data(data)
    except Exception as e:
        if options.continue_on_file_errors:
            return
        else:
            raise

    for e in selector(dom):
        context = get_context(dom, e, anchors)

        print_record(formatter.format_record(map(lambda t: compute_value(t, context), terms)))


def screp_all(formatter, terms, anchors, selector, sources):
    print_record(formatter.start_format())

    for source in sources:
        screp_source(formatter, terms, anchors, selector, source)

    print_record(formatter.end_format())


def make_data_source(source):
    url = urlparse.urlparse(source)

    if url.scheme != '':
        return URLDataSource(source)
    else:
        return FileDataSource(source)


def parse_cli_options(argv):
    parser = OptionParser()

    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False, help='verbose')
    parser.add_option('-n', '--null-value', dest='null_value', action='store',
            default='NULL', help='value to print when a value cannot be computed')
    parser.add_option('-e', '--stop-on-error', dest='stop_on_error', action='store_true',
            default=False, help='stop on first error; inhibits --null-value')
    parser.add_option('-c', '--csv', dest='csv', action='store', default=None,
            help='print record as csv row')
    parser.add_option('-F', '--continue-on-file-errors', dest='continue_on_file_errors',
            action='store_true', default=False, help='ignore errors in opening and reading data sources')
    parser.add_option('-a', '--anchor', dest='anchors', action='append', default=[],
            help='define secondary anchor, relative to the primary anchors, using the format <name>=<term>')
    parser.add_option('-H', '--csv-header', dest='csv_header', action='store',
           default=None, help='print csv header')
    parser.add_option('-d', '--debug', dest='debug', action='store_true', default=False,
            help='print debugging information on errors; implies -e')
#   parser.add_option('-j', '--json', dest='json', action='store',
#           default=None, help='print record as json object')
#   parser.add_option('-f', '--format', dest='format', action='store',
#           default=None, help='print record as custom format')
#   parser.add_option('-U', '--base-url', dest='base_url', action='store',
#           default=None, help='base url to use when computing absolute urls')

    (options, args) = parser.parse_args(argv)

    if len(args) == 0:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    selector = args[0]

    if len(args) == 1:
        sources = [OpenedFileDataSource('STDIN', sys.stdin)]
    else:
        sources = map(make_data_source, args[1:])

    return (options, selector, sources)


def main():
    global options

    try:
        (options, selector, sources) = parse_cli_options(sys.argv[1:])

        (formatter, terms) = get_formatter()

        anchors = map(get_anchor, options.anchors)

        selector = get_selector(selector)

        screp_all(formatter, terms, anchors, selector, sources)

    except Exception as e:
        if options.debug:
            raise
        else:
            report_error(e)

        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
