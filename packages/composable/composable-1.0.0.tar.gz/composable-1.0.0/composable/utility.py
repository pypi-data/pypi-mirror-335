from composable import pipeable
from toolz import get as toolz_get
from inspect import getdoc

base_dir = dir
base_help = help

def identity(x):
    """ The identify function.
    """
    return x

@pipeable
def dir(obj = None, *, hide_underscores = True):
    """ Replacement for `dir` that returns a list of attributes and hides underscored/dunder 
    items by default.

    Args.
        - obj: An optional object/class [default = None]
        - hide_underscores: Whether to hide attributes starting with an underscore.

    Returns: A list of strings, one for each method.  If no `obj` is provided, returns 
             the names in the main/current namespace.
    """
    if obj:
        return [m 
                for m in base_dir(obj) 
                if not hide_dunder or m.startswith('_')
               ]
    else:
        return [m 
                for m in base_dir() 
                if not hide_dunder or m.startswith('_')
               ]

@pipeable
def try_(try_func, except_func, obj):
    """ A functional replacement for the try/except statement.

    Args.
        - try_func: A single argument function executed in the try block.
        - except: A single argument function executed in the except block which
                  receives any exception as an argument.
        - obj: Argument passed to `try_func` in the try block.

    Returns: The result of the try/except block, 
             either a return value (try) or an exception (except).
    """
    try:
        return try_func(obj)
    except e:
        return except_func(e)

@pipeable
def get(ind, seq, default='__no__default__'):
    getdoc(toolz_get)
    return toolz_get(ind, seq, default)

@pipeable
def with_(body_func, context):
    """ Functional replacement for a with statement.

    Args.
        - body_func: The single argument function executed in the body of the with block.
                     Recieves a handle to the context object.
        - context: The context imbedded in the with statement.

    Note.  This is equivalent to the following
        > with context as c:
        >     return body_func(c)

    Returns. The output of `body_func` executed on the context handle.
    """
    with context as c:
        return body_func(c)

@pipeable 
def with_open(body_func, 
              file,
              *,
              mode='r',
              buffering=-1,
              encoding=None,
              errors=None,
              newline=None,
              closefd=True,
              opener=None,
             ):
    """ Functional replacement for a with statement containing `open`.

    Args.
        - body_func: The single argument function executed in the body of the with block.
                     Recieves a handle to the context object.
        - file: file path imbedded in `open`
        - ... Additional arguments passed to open, see `help(open)` for more info.

    Note.  This is equivalent to the following
        > with open(file) as f:
        >     return body_func(f)

    Returns. The output of `body_func` executed on the file handle.
    """
    with open(file,
              mode,
              buffering,
              encoding,
              errors,
              newline,
              closefd,
              opener,
             ) as f:
        return body_func(f)
    

@pipeable
def apply(func, value):
    """ Apply a function to a value, possibly by piping with `>>`

    Args.
        - func: The single-argument function to be applied.  This function need not be 
                pipeable.
        - value: The input argument

    Returns: The result of `func(value)`
    """
    return func(value)
    