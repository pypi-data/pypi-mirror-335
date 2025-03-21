from .pipeable import pipeable

@pipeable
def split_by(funcs, obj):
    ''' Applies a sequence of funcs to obj, returning a tuple

    Args:
        - funcs: A sequence of unary functions
        - obj: Any object

    Returns: A tuple of return values, obtained by applying the funcs to obj.

    >>> from composable.tuple import split_by
    >>> 1 >> split_by((str, float))
    ('1', 1.0)
    >>> from composable.strict import map
    >>> range(3) >> map(split_by((str, float)))
    [('0', 0.0), ('1', 1.0), ('2', 2.0)]
    '''
    return tuple(f(obj) for f in funcs)