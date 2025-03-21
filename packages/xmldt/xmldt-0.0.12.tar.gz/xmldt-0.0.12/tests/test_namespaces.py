from pprint import pprint
from xmldt import XmlDt


def test_ignore():

    class X (XmlDt):
        meta_was_called = False

        def meta(self, element):
            self.meta_was_called = True

    # _root.nsmap = {None: 'http://www.tei-c.org/ns/1.0', 'dacl': 'http://dacl.zbr.pt/annotations'}
    parser = X(ns_strip=True)
    parser(filename="tests/namespaces.xml")
    assert parser.meta_was_called

