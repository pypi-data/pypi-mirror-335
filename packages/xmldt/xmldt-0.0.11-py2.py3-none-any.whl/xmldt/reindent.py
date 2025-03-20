""" removes initial indentation.

# Synopsys

  r= reindent(f'''
       def.....
          .....
       ''')

# Description

The indentation found in first line, is removed from all the other lines.

If newindent is provided, (' ' * newindent) is inserted in the begining of
    all the lines.

## Other functions ( printstr* = io.stringIO + reindent )

   1)   x = printstrinit("")    ## new strIO x
   2.1) printstr(x,"potatoes","and","other")  ## add to x
   2.3) printstrri(x, '''       
            def f ():
              ...
            ''')                ## add a reindented str to x
   3)   z = printstrval(x)      ## get the value and closeit
"""

import re
import io


def reindent(s, newindent=0):
    """ removes initial indentation.
    The indentation found in first line, is removed from all the other lines.

    If newindent is provided, (' ' * newindent) is inserted in the begining of
    all the lines.
"""

    s = re.sub(r"^(?=.)",r'\n',s)               # ensure initial \n
    indent = re.match(r'\n+([ \t]*)', s)[1]     # get indent of line1
    s = re.sub(rf"\n{indent}$",r'',s)           # rem final \nindent
    s = re.sub(rf"\n{indent}",rf'\n{" " * newindent}',s)  # reindent
    s = re.sub(rf"^\n",r'',s)                   # remove inicial empty line
    return s


def printstrinit(s="", newindent=0):
    output = io.StringIO()
    print(reindent(s,newindent), file=output)
    return output

def printstrri(output,s, newindent=0):
    print(reindent(s,newindent), file=output)

def printstr(output,*args, **kwargs):
    print(*args, file=output, **kwargs)

def printstrval(output):
    contents = output.getvalue()
    output.close()
    return contents
