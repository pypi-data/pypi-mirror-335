# Changelog

### 0.0.11 - March 19th, 2025

 - bug fixed: `_types = {"t": "map"...}` were ignoring `ns_strip` flag 

### 0.0.9 - August 2nd, 2024

 - rename father/gfather by parent/gparent

### 0.0.8 - June 12th

 - Added `proc(url="http://...")`  xml input from a URL
   ( and `tests/teste_dturl` )
 - Added possibility of configurate flags in the Class.
   - example: `_flags = { "empty"=True ...}`

 - Rename methods from items to `dt_*` methods/properties
 - Added `ns_strip` option (`True` by default)

### 0.0.6 - February 11th

 - Added `chain` method
 - Added `hooks` and `add_hook` methods
 - `pydt` changes:
   - detection of mixed-PCDATA elements
   - `-i` shows a new tree with compact repeated elements
   - support for tags with dashes
   - `-a` and `--average-pcdata` were renamed to `-l`, `--len` or
     `--average-pcdata-len`.
   - added `-a`/`--all` to activate `-l` and `-i`
   - support older `argparse` versions
   - added `--html` option

### 0.0.5 - January 24th

 - `pydt` new interface:
   - `-i` or `--indent` to indent function names
   - `-d` or `--debug` to activate debug
   - `-n` or `--name` to set the processor name
   - `-a` or `--average-pcdata` to compute pcdata average length
 - Fixed element.root accessor
 - Added support for custom class processing

### 0.0.4 - January 22nd

 - Renamed main class to XmlDt
 - Created class for parsing HTML: HtmlDt
 - Fixed behavior for 'zero' type

### 0.0.3 - January 20th

 - Added support for tag-names with non valid method characters
 - Added support for types
 - Added support for HTML files 
 - pydt: added support for multiple input files (pydt f1.xml f2.xml ...)
 - Added recovery flag
 - Added support for comments (ignored by default, but can be processed)

### 0.0.2 - January 4th

 - Fixed pydt command
 - Added support to the `@XMLDT.tag` decorator
 - Added tests to _Skel_ code
 - Support for `father` and `gfather` accessors

### 0.0.1

 - First version
