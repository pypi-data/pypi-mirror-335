import pytest
import sys
from xmldt import XmlDt
from lxml.etree import XMLSyntaxError



def test_simple_file():
    class T1 (XmlDt):
        pass

    t1 = T1(strip=True, empty=False, recover=False)
    with pytest.raises(XMLSyntaxError, match="Opening and ending tag mismatch"):
        # lxml.etree.XMLSyntaxError: Opening and ending tag mismatch
        t1(filename="tests/norecover.xml")



