
# xmldt

This python 3 module is a reimplementation of the long living Perl module `XML::DT`.
It was rewritten taking in mind the pythonic way of writing code, but
guaranteeing the Down-Translate approach to process XML.

### Installing

Use `pip` to install the stable version

    $ pip install xmldt

### Synopsis

Start bootstrapping a processor using the `pydt` script:

    $ pydt -s sample.xml > sample_processor.py

### Functions and Classes

#### Class Element

    e.tag          or e.q
    e.attributes   or e.v
    e.contents     or e.c
    e.parent
    e.gparent
    e.root
    e.xml          <e.q e.v> e.c</e.q>

#### Class XmlDt

    def tag(self, e):         ## for all tags
    def __default__(self, e)  ## used for undefined tag proc. (default: toxml)
    def __pcdata__(self, t):  ## proc for pctada (default: id)
    def __end__(self, t):     ## final processor (default: id)

### Contributing

 * to test: `pytest`
 * to check coverage: `pytest --cov`
 * to generate coverage report in HTML: `pytest --cov --cov-report=html`

### TODO

 * process multiple XML files at once
 * access parent from pcdata
 * look to the possibility of a `__begin__`
