from .pipeable import pipeable
from typing import Literal
from toolz import identity


@pipeable
def split_by(funcs, obj):
    ''' Create a dictionary by applying a dict of funcs to a base obj.
    
    Equivalent to {k: f(obj) for k, f in funcs.items()}
    Args:
        - funcs: A dictionary of key, unary func pairs to be applied to obj
        - obj: Base object to apply functions
        
    Returns: a dictionary of key, return values

    >>> from composable.dict import split_by
    >>> fs = {'s':str, 'f': float}
    >>> 1 >> split_by(fs)
    {'s': '1', 'f': 1.0}
    >>> from composable.strict import map
    >>> range(3) >> map(split_by(fs))
    [{'s': '0', 'f': 0.0}, {'s': '1', 'f': 1.0}, {'s': '2', 'f': 2.0}]
    '''
    return {k:f(obj) for k, f in funcs.items()}

DictApplyStrategy: Literal = Literal['drop_both',
 'keep_both', 
 'drop_missing_values', 
 'drop_missing_functions']


def apply(funcs, 
          d, 
          missing: DictApplyStrategy='keep_both', 
          default_value = None, 
          default_func=identity):
    '''Apply a dictionary of functions the value of matching keys in d.
       Values of d for keys missing from funcs remain unchanged when drop_missing=False,
       but get dropped otherwise.

    Equivalent to 
        - drop_missing = False
            {k: funcs[k](val) if k in funcs else val 
            for k, val in d.items}
        - drop_missing = True
            {k: funcs[k](val)
            for k, val in d.items
            if k in f}
    Args:
        - funcs: A dictionary of key, unary function pairs.
        - d: A dictionary of values
    
    '''
    raise NotImplemented