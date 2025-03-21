from .pipeable import pipeable
from typing import Callable, Optional, TypeVar

A = TypeVar('A')
B = TypeVar('B')

@pipeable
def map(f, L):
    ''' applies f to all elements of L, immediately returning a list of the resulting values.

    Equivalent to [f(x) for x in L]
    Args:
        f: A unary function
        L: A list of values

    Returns:
        A list of the results of f applied to each element of L.
        Note that this is a strict version of the built-in map (which returns a generator).

    >>> from composable.strict import map
    >>> range(3) >> map(lambda x: x + 5)
    [5, 6, 7]
    '''
    return [f(x) for x in L]

__builtin_sorted = sorted


@pipeable
def sorted(iterable, /, *, key=None, reverse=False):
    '''Return a new list containing all items from the iterable in ascending order.

    A custom key function can be supplied to customize the sort order, and the
    reverse flag can be set to request the result in descending order.

    Args:
        - iterable: Any iterable sequence
        - key: a callable/function used to compare items.
        - reverse: Whether or not the sequence should be reversed

    >>> from composable.strict import sorted
    >>> vals = [3, 2, 1, 5, 4]
    >>> vals >> sorted()
    [1, 2, 3, 4, 5]
    >>> vals >> sorted(reverse=True)
    [5, 4, 3, 2, 1]
    '''
    return __builtin_sorted(iterable, key=key, reverse=reverse) 


@pipeable
def star_map(f, L):
    ''' applies f after unpacking the elements of L as positional arguments, immediately returning a list of the resulting values.

    Equivalent to [f(*args) for args in L] 
    Args:
        f: A function taking one or more positional arguments
        L: A list of tuples of values to be unpacked when calling f

    Returns:
        A list of the results of f applied to each element of L.
        Note that this is a strict version of the built-in map (which returns a generator).

    >>> from composable.strict import star_map
    >>> from operator import add
    >>> vals = list(zip(range(5), range(2, 7)))
    >>> vals
    [(0, 2), (1, 3), (2, 4), (3, 5), (4, 6)]
    >>> vals >> star_map(add)
    [2, 4, 6, 8, 10]
    '''
    return [f(*args) for args in L]


@pipeable
def filter(p, L):
    ''' Filters the elements of L, returning a list of all elements that pass the predicate p.

    Args:
        p: a unary boolean function used to filter the list
        L: A list of values

    Returns:
        A list of the elements of L that satisfy p.
        Note that this is a strict version of the built-in filter (which returns a generator).
    '''
    return [x for x in L if p(x)]


@pipeable
def zipWith(iter2, iter1):
    ''' zips the elements of iter1 and iter2 into a list of tuples of the form (i1, i2)

    args:
        iter2: a list of values
        iter1: a list of values

    returns:
        a list of tuples of the form (i1, i2).  this is similar to zip(iter1, iter2).
        note that
        1. the order is reversed for more natural piping, 
           that is iter1 >> zipwith(iter2) has the values of iter1 first, i.e. (i1, i2)
        2. performs strict application, where the built-in zip returns a generator.
    '''
    return [ (i1, i2) for i2, i1 in zip(iter2, iter1)]


@pipeable
def zipOnto(iter1, iter2):
    ''' zips the elements of iter1 and iter2 into a list of tuples of the form (i2, i1)

    args:
        iter1: a list of values
        iter2: a list of values

    returns:
        a list of tuples of the form (i2, i1).  this is similar to zip(iter1, iter2).
        note that
        1. the order is the same as the built-in zip, meaning piping will reverse the order
           that is iter1 >> zipOnto(iter2) has the values of iter1 first, i.e. (i2, i1)
        2. performs strict application, where the built-in zip returns a generator.
    '''
    return list(zip(iter1, iter2))

enum = enumerate

@pipeable
def enumerate(iter):
    ''' generates a list of tuples, pairing each value with its index, (index, value)

    Args:
        iter: A sequence of values

    Returns:
        A list of tuples of the form (index, value), which correspond to the index and value
        of each entry of iter.
        Note that this is a strict version of the built-in enumerate (which returns a generator).
    '''
    return list(enum(iter))


@pipeable
def split_by(funcs: list[Callable[[A], B]], obj:A) -> list[B]:
    '''Apply each of a list of functions to an object, returning the list of results.
    
    Args:
        - funcs: A list of functions.
        - obj: Object to use as an argument.
        
    Returns: List of return values.

    Example:

    >>> from composable.strict import split_by
    >>> from toolz.curried.operator import add, mul
    >>> 3 >> split_by([add(1), add(2), mul(3)])
    [4, 5, 9]
    '''
    return [f(obj) for f in funcs]
