import pytest
from xmldt import XmlDt
import sys
from pprint import PrettyPrinter as pp


def test_id1():
    class T1 (XmlDt):
        pass

    tests = (
        "<foo>0</foo>",
        "<foo>0<bar>0</bar>0</foo>",
        "<foo>bar</foo>",
        "<foo>zbr<bar>ugh</bar>eck</foo>",
        '<foo><bar zbr="ugh"/></foo>',
    )
    t1 = T1()
    for xml in tests:
        assert t1(xml) == xml


def test_keep_empty_jj():
    class T3 (XmlDt):
        _flags = { "empty": True }

    assert T3()("<foo>  </foo>") == "<foo>  </foo>"
    assert T3(empty=True)("<foo>ver <link>aqui</link></foo>") == "<foo>ver <link>aqui</link></foo>"
    assert T3(empty=False)("<foo>  </foo>") == "<foo>  </foo>"    # empty=True is forced in class

def test_keep_empty():
    class T3 (XmlDt):
        pass

    assert T3(empty=True)("<foo>  </foo>") == "<foo>  </foo>"
    assert T3(empty=True)("<foo>ver <link>aqui</link></foo>") == "<foo>ver <link>aqui</link></foo>"
    assert T3(empty=False)("<foo>  </foo>") == "<foo/>"    # for now this is the default behavior


def test_keep_empty__new():
    class T4 (XmlDt):
        pass

    assert T4("<foo>  </foo>", empty=True) == "<foo>  </foo>"
    assert T4("<foo>ver <link>aqui</link></foo>", empty=True) == "<foo>ver <link>aqui</link></foo>"
    assert T4("<foo>  </foo>") == "<foo/>"    # for now this is the default behavior


def test_default_and_join():
    class T2 (XmlDt):
        def __join__(self, child):
            return child

        def __default__(self, element):
            return [element.tag, element.contents]

    tests = (
        ("<foo>bar</foo>", ["foo", ["bar"]]),
        ("<foo>zbr<bar>ugh</bar>eck</foo>", ["foo", ["zbr", ["bar", ["ugh"]], "eck"]]),
        ('<foo><bar zbr="ugh"/></foo>', ["foo", [["bar", []]]]),  # not practical, but makes sense
    )
    for xml, strut  in tests:
        assert T2()(xml) == strut


def test_path_and_parent():
    class T3 (XmlDt):
        def foo(self, element):
            assert element.parent is None
            assert element["gparent"]
            assert element["root"]
            return ""

        def bar(self, element):
            assert element["parent"]
            return ""

        def zbr(self, element):
            assert element.gparent.tag == "foo"
            assert element.in_context("bar")
            assert not element.in_context("xpto")
            assert len(element.path) == 2
            element.parent["parent"] = True
            element.gparent["gparent"] = True
            element.root["root"] = True
            return ""

    T3()("<foo>aaa<bar>bbb<zbr>ccc</zbr>bbb</bar>aaa</foo>")


def test_tag_decorator():
    class T1 (XmlDt):
        @XmlDt.dt_tag("foo")
        def xpto(self, e):
            return "batatas"

    class T2 (XmlDt):
        def foo(self, e):
            return "cebolas"

    assert T1()("<foo></foo>") == "batatas"
    assert T2()("<foo></foo>") == "cebolas"
