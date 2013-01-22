

def test_location_factory_context():
    import screp.term_parser as term_parser
    import screp.idloc as idloc

    with term_parser.location_factory_context(idloc.LocationFactory('SOURCE', index_offset=11)):
        loc = term_parser.make_location(5)

        assert type(loc) is idloc.Location
        assert loc.source == 'SOURCE'
        assert loc.index == 16


    loc = term_parser.make_location(5)

    assert type(loc) is idloc.Location
    assert loc.source != 'SOURCE'


class TestLocationFactory(object):
    def test_make_location(self):
        import screp.idloc as idloc

        factory = idloc.LocationFactory('SOURCE', index_offset=-10)

        location = factory.make_location(4)

        assert type(location) is idloc.Location

        assert location.source == 'SOURCE'

        assert location.index == -6
