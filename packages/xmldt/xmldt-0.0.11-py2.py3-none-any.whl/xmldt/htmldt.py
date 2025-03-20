from xmldt import XmlDt
from collections import OrderedDict
import re

# will look into https://docs.python.org/3/library/inspect.html later


class HtmlDt (XmlDt):

    # at the moment we can't guarantee any order, so only one of the existing classes is run
    @classmethod
    def html_class(cls, name):
        def decorator(func):
            def tmp(*args, **kwargs):
                return func(*args, **kwargs)

            tmp.has_class = name
            return tmp
        return decorator

    def __init__(self, **kwargs):
        super().__init__(**{**kwargs, "html": True})  # couldn't rewrite better
        self._classes = {
            method.has_class: method for method in {
                getattr(self, name) for name in dir(self)
                if callable(getattr(self, name)) and hasattr(getattr(self, name), "has_class")}}
        self.dt_add_hook(self._class_hook)

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **{**kwargs, "html": True})

    def _class_hook(self, element):
        handlers = []
        if "class" in element:
            element["class"] = re.split(r'\s+', element["class"])
            for c in element["class"]:
                if c in self._classes:
                    handlers.append(self._classes[c])
        return handlers


