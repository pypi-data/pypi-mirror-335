from xmldt.skel import build_skel
import sys
import re


def test_build_skel():
    skel = build_skel(["tests/test1.xml"])

    # print(skel, file=sys.stderr)
    assert type(skel) is str
    assert re.search(r"def __default__", skel)
    assert re.search(r"# def body", skel)
    assert re.search(r"# def root", skel)


def test_build_skel_indent():
    skel = build_skel(["tests/test1.xml"], indent=True)

    # print(skel, file=sys.stderr)
    assert type(skel) is str
#    assert re.search(r"def __default__", skel)
#    assert re.search(r"# def    body", skel)   # check indentation
#    assert re.search(r"# def root", skel)


def test_build_skel_average_pcdata():
    skel = build_skel(["tests/test1.xml"], average_pcdata=True)

    # print(skel, file=sys.stderr)
    assert type(skel) is str
    assert re.search(r"# def body.*len\(27\)", skel)


def test_build_skel_annotation():
    skel = build_skel(["tests/test3.xml"], average_pcdata=True)

    # print(skel, file=sys.stderr)
    assert re.search(r"""# @XmlDt.dt_tag\("some.tag"\)""", skel)
    assert re.search(r"""# def some_tag""", skel)
