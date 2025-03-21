import pytest
from xmldt import XmlDt
import sys
from pprint import PrettyPrinter as pp


def test_id1():
    class T1 (XmlDt):
        pass

    assert "browse projects" in T1(url="https://pypi.org")
