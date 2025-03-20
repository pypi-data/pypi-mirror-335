"""
  python module to Down Translate XML

Synopsis
========

# Description

"""
__docformat__ = 'markdown'

from lxml.etree import XMLParser, parse, fromstring, Comment, HTMLParser
from xmldt.element import Element, toxml
import sys, re
import urllib.request

__version__ = "0.0.11"


class XmlDt:

    @classmethod
    def dt_tag(cls, name):   # FIXME: este metodo esta a poluir o namespace...
        def decorator(func):
            def tmp(*args, **kwargs):
                return func(*args, **kwargs)

            tmp.has_alias = name
            return tmp
        return decorator

    def __init__(self, strip=False, empty=False, html=False, ns_strip=True):
        self._parser = XMLParser(recover=True) if not html else HTMLParser(recover=True)
        self._chaining = None
        self._path = []
        self._hooks = []

        default_flags = {
            "strip": strip,
            "ns_strip": ns_strip,
            "empty": empty
        }
        cur_flags = getattr(self, "_flags", {})       ## _flags defined in the class if present
        self._flags = { **default_flags, **cur_flags } ## FIXME: parameter priority ?

        self._types = getattr(self, "_types", {})
        self._alias = {
            method.has_alias: method for method in {
                getattr(self, name) for name in dir(self)
                if callable(getattr(self, name)) and hasattr(getattr(self, name), "has_alias")}}

    def __new__(cls, xml=None, filename=None, url=None, strip=False, empty=False, html=False, ns_strip=True):
        
        # nao gosto, mas funciona
        self = super(XmlDt, cls).__new__(cls)
        self.__init__(strip=strip, empty=empty, html=html, ns_strip=ns_strip)

        if filename is not None or xml is not None or url is not None:
            return self(xml, filename, url)
        else:
            return self

    def __call__(self, xml=None, filename=None, url=None):
        if filename is not None:
            
            self._tree = parse(filename, parser=self._parser)
            self._tree = self._tree.getroot()
        elif xml is not None:
            self._tree = fromstring(xml, parser=self._parser)
        elif url is not None:
            with urllib.request.urlopen(url) as u:
                htmltxt = u.read()
            self._tree = fromstring(htmltxt, parser=self._parser)
        else:
            raise Exception("DT called without arguments")
        return self.__end__(self._recurse_node(self._tree))

    def __pcdata__(self, text):
        """Method called to process text nodes. If you override it, call its superclass method to
           guarantee empty and strip options to be honored"""
        if not self._flags["empty"] and str.isspace(text):
            return None
        if self._flags["strip"]:
            text = text.strip()
        return text

    def __default__(self, element):
        """Default handler for XML elements, when no specific handler is defined"""
        return element.xml

    def __end__(self, result):
        """Handler called after DT process, so it can be used for final processing tasks"""
        return result

    def __comment__(self, text):
        """Handles comment texts. Returns None by default"""
        return None

    def _recurse_node(self, element):

        # copy attributes, so we can store whatever object we want
        if element.tag is Comment:
            comment = self.__comment__(element.text)
            return comment
        else:
            tag_name = re.sub(r'{[^}]+}', "", element.tag) if self._flags["ns_strip"] else element.tag
            #tag_type = "string" if tag_name == "-pcdata" else self._types.get(tag_name, "maybestr")
            tag_type = self._types.get(tag_name, "string")

            if tag_type == "zero":  # ignore and skip children
                return ""

            # add to path only if required
            self._path.append(Element(tag_name, {**element.attrib}, None, self))

            tag_handlers = []
            for hook in self._hooks:
                tag_handlers += hook(self._path[-1])

            if tag_name in self._alias:
                tag_handlers.append(self._alias[tag_name])
            else:
                handler = getattr(self, tag_name, None)
                if handler is not None and callable(handler):
                    tag_handlers.append(handler)

            tag_handlers.append(self.__default__)

            # given an element, process children, returning a list of pairs
            contents = self._dt(element)      # not zero:
            elem = self._path.pop()

##            if tag_type == "maybestr" and len(contents) == 1 and isinstance(contents[0],(list, dict, tuple)):
##                elem.c = contents[0]

##            elif tag_type == "string" or tag_type == "maybestr":
            if tag_type == "string" :
                c_list = [ele for t, ele in contents if ele]   # FIXME?? Caso do 0 ???
                elem.c = self.__join__(c_list)

            elif tag_type == "list":
                elem.c = [e for t, e in contents]

            elif tag_type == "map":
                if self._flags["ns_strip"]:
                    elem.c = {re.sub(r'{[^}]+}', "", t): e for t,e in contents }
                else: 
                    elem.c = {t : e for t,e in contents }

            elif tag_type == "mmap":
                raux = {}
                for t, e in contents:
                    if self._flags["ns_strip"]: t= re.sub(r'{[^}]+}', "",t)
                    if t in raux:
                        raux[t].append(e)
                    else:
                        raux[t] = [e]
                elem.c = raux

            elif tag_type == "mmapwn":
                raux = {}
                for t, e in contents:
                    if self._flags["ns_strip"]: t= re.sub(r'{[^}]+}', "",t)
                    if t in raux:
                        raux[t].append(e)
                    else:
                        raux[t] = [e]
                
                for t, e in raux.items():
                    if len(e) == 1:
                        raux[t] = e[0]

                elem.c = raux

            else:
                raise Exception(f"Element type not recognized: {tag_type}")

            result = None  # should never happen, default is always there
            for handler in tag_handlers:
                self._chaining = None
                result = handler(elem)
                if self._chaining is not None:
                    elem = self._chaining
                    self._chain = False
                else:
                    break

            return result

    def _dt(self, tree):
        children = []    # agora retorna lista de pares (tag, conte)*
        if tree.text:
            r = self.__pcdata__(tree.text)
            if r:  # should we check for None or "" ?
                children.append(("-pcdata", r))

        for child in tree:
            children.append((child.tag, self._recurse_node(child)))
            if child.tail:
                r = self.__pcdata__(child.tail)
                if r:  # should we check for None or "" ?
                    children.append(("-pcdata", r))
        return children

    def __join__(self, child):
        if len(child) == 1: 
            return child[0]
        return str.join("", [str(x) for x in child])

    def dt_chain(self, elem):
        self._chaining = elem

    def dt_in_context(self, tag):
        return len([e for e in self._path if e.tag == tag]) > 0

    def dt_add_hook(self, hook):
        self._hooks.insert(0, hook)

    @property
    def dt_hooks(self):
        return self._hooks

    @property
    def dt_path(self):
        return self._path

    @property
    def dt_parent(self):
        return None if len(self._path) < 1 else self._path[-1]

    @property
    def dt_gparent(self):
        return None if len(self._path) < 2 else self._path[-2]

    @property
    def dt_root(self):
        return None if len(self._path) < 1 else self._path[0]
