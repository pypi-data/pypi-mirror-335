import sys

from xmldt import XmlDt
from xmldt.reindent import *
import argparse
import re
from collections import OrderedDict as odict


def build_skel(files, name="proc",
               indent=False,
               debug=False,
               html=False,
               ini="_ROOT",
               average_pcdata=False):

    skel = Skel(html=html)
    skel.flags = {"debug": debug}
    for filename in files:
        skel(filename=filename)

    if indent:
        return _dump_odict(skel,ini,withdef=False)

    dump2 = dumpdefs(skel, name, debug,html,ini,average_pcdata)

    return dump2

def dumpdefs( skel, name="proc",
               debug=False,
               html=False,
               ini="_ROOT",
               average_pcdata=False):

    supcl = "HtmlDt" if html else "XmlDt"

    code = printstrinit( f"""
        #!/usr/bin/python3
        from xmldt import {supcl}, toxml
        import sys
        class {name} ({supcl}):
            pass

            # def __default__(s, e): 
            #     return f"[tag: {{e.tag}}, contents: {{e.c}}, attr: {{e.v}}]"
        """)

    for tag in skel.order:
        v = skel.data[tag]
        attrKeys = v.keys() - {":count", ":pcdata"}
        attrs = str.join(" ", [f"{a}({v[a]})" for a in attrKeys])
        if ":pcdata" in v:
            pcdatalen = ""
            mix = ""
            if average_pcdata:
                pcdatalen = v[':pcdata'] // v[':count']
                pcdatalen = f" len({pcdatalen})"
                
            if tag in skel.suns:
                mix = "mixed-"
            cont = f"{v[':count']} {attrs} {mix}PCDATA{pcdatalen}"
        else:
            cont = f"{v[':count']} {attrs}"

        method = re.sub(r"\{.*?\}", r"", tag)
        method = re.sub(r"[.\-]", r"_", method)

        if method != tag:
            printstrri(code, f'# @XmlDt.dt_tag("{tag}")',4)

        printstrri(code, f"# def {method}(s, e):   # {cont}",4)

    printstrri(code,f'''

        file = sys.argv[1]
        print({name}(filename=file))    # , empty=True
        ''')

    return printstrval(code)



class Skel (XmlDt):
    data = {}              # tag → (attr | # → int)
    ans = {}               # ancestors tag → tag-path  (of first oco)
    suns = odict({"_ROOT":odict()})              # tag → set(tag)
    order = []             # list(tag)
    path_order = []
    flags = {}

    def _debug(self, *msgs):
        if self.flags["debug"]:
            print("DEBUG: ", *msgs, file=sys.stderr)

    def __pcdata__(self, e):
        if e.isspace(): return ""
        self.dt_path[-1][":pcdata"] = (self.dt_path[-1][":pcdata"] or 0) + len(e)

        self._debug(f"{e} {len(e)}")

    def __default__(self, e):
        # FIXME testing
        
        p = [a.tag for a in self.dt_path] + [e.tag]
        _ensure_add_odict(self.suns, p )
        if e.tag not in self.data:
            self.ans[e.tag] = p[:-1]
                ## p = self.ans[e.tag] = [a.tag for a in self.dt_Path]
            for tag in p:
                if tag in self.order:
                    continue
                self.order.append(tag)
            self.data[e.tag] = {":count": 0}
        self.data[e.tag][":count"] += 1
        for key in e.attrs.keys():
            if key not in self.data[e.tag]:
                self.data[e.tag][key] = 0
            if key == ":pcdata":
                self.data[e.tag][key] += e[":pcdata"]  # len of text
            else:
                self.data[e.tag][key] += 1

def _dump_odict_compact(skel, ini, vis=set(), lev=0):  
    """ ordered dict compact """

    suns = skel.suns
    r = ini
    if ini in vis:
        ini_suns = "[...]" if ini in suns else ""
        return f"{r}{ini_suns}"

    vis.add(ini)
    if ini in suns:
        l = [ _dump_odict_compact(skel, ele, vis, lev+1) for ele, v in suns[ini].items() ] 
        lstr = str.join(" ",l)
        r =  f"{r} [ {lstr} ]"
    return r


def _dump_odict(skel, ini="_ROOT", vis=set(), lev=0, withdef=None):
    """ ordered dict with # ... for repetitions """

    suns = skel.suns
    attrs = "" 
    if ini != "_ROOT":
        v  = skel.data[ini]
        ks = v.keys() - {":count", ":pcdata"}
        if len(ks) != 0:
            attrs = " ( " + str.join(" ", [f"{a}({v[a]})" for a in ks]) + " )"

    r = ""
    if ini in vis:
        compact = _dump_odict_compact(skel, ini, set(), lev)
        if withdef:
            r += f"# ... {'   '*lev}{compact}" + "\n"
        else:
            r += f"{'   '*lev}...{compact}" + "\n"
    else:
        if withdef:
            r += f"# def {'   '*lev}{ini}(s, e):" + "\n"
        else:
            r += f"{'   '*lev}•  {ini}{attrs}" + "\n"

    if ini not in vis:
        vis.add(ini)
        if ini in suns:
            for ele, v in suns[ini].items(): 
                r += _dump_odict(skel, ele, vis, lev+1, withdef)
    return r


def _add_odict(suns, a, b):
    """ add "a has-sun b" to suns """ 

    if not a:
        suns["_ROOT"] = odict({b: 1})
    else:
        if a in suns:
            suns[a][b] = 1
        else:
            suns[a] = odict({b: 1})


def _ensure_add_odict(suns, path):
    """ element path --> suns """

    _add_odict(suns,None, path[0])
    for i in range(len(path)-1):
        _add_odict(suns,path[i],path[i+1])


def _ensure_path(seq, path):
    for i in range(len(path)):
        t = tuple(path[:i+1])
        if t not in seq:
            seq.append(t)


def main():
    arg_parser = argparse.ArgumentParser( 
          description= "Builds a xmldt processor skeleton from a xml example",
          epilog= reindent(""" 
             tbp
                ... 
             """))
    arg_parser.add_argument("filename", type=str, nargs='+', 
          help="the XML files to use as model")
    arg_parser.add_argument("-i", "--indent", action="store_true", default=False, 
          help="Indent element tree")
    arg_parser.add_argument("-r", "--root", type=str, default="_ROOT",
          help="show only element inside ROOT")
    arg_parser.add_argument("-n", "--name", type=str, default="proc",
          help="the name for the resulting class (def:'proc')")
    arg_parser.add_argument("-f", "--full",  action="store_true",
          help="full tree")
    arg_parser.add_argument("-H", "--html",  action="store_true", 
          help="HTML input")
    arg_parser.add_argument("-d", "--debug", action="store_true", default=False, 
          help="activate debug")
    arg_parser.add_argument("-l", "--average-pcdata-len", "--len", action="store_true", default=False, 
          help="compute pcdata length average")
    arg_parser.add_argument("-a", "--all", action="store_true", default=False, 
          help="Activate -i and -l")

    args = arg_parser.parse_args()

    print(build_skel(args.filename,
                     indent=args.indent or args.all,
                     average_pcdata=args.average_pcdata_len or args.all,
                     name=args.name,
                     html=args.html,
                     ini=args.root,
                     debug=args.debug))

def main_xmldttree():
    arg_parser = argparse.ArgumentParser( 
          description= "Builds a xmldt processor skeleton from a xml example",
          epilog= reindent(""" 
             tbp
                ... 
             """))
    arg_parser.add_argument("filename", type=str, nargs='+', 
          help="the XML files to use as model")
    arg_parser.add_argument("-i", "--indent", action="store_true", default=False, 
          help="Indent element tree")
    arg_parser.add_argument("-r", "--root", type=str, default="_ROOT",
          help="show only element inside ROOT")
    arg_parser.add_argument("-n", "--name", type=str, default="proc",
          help="the name for the resulting class (def:'proc')")
    arg_parser.add_argument("-f", "--full",  action="store_true",
          help="full tree")
    arg_parser.add_argument("-H", "--html",  action="store_true", 
          help="HTML input")
    arg_parser.add_argument("-d", "--debug", action="store_true", default=False, 
          help="activate debug")
    arg_parser.add_argument("-l", "--average-pcdata-len", "--len", action="store_true", default=False, 
          help="compute pcdata length average")
    arg_parser.add_argument("-a", "--all", action="store_true", default=False, 
          help="Activate -i and -l")

    args = arg_parser.parse_args()

    print(build_skel(args.filename,
                     indent=True,
                     average_pcdata=args.average_pcdata_len or args.all,
                     name=args.name,
                     html=args.html,
                     ini=args.root,
                     debug=args.debug))
