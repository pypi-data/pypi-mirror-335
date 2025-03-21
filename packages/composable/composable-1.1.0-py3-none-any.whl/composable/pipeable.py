from inspect import signature
from functools import reduce
from toolz import first, drop
from toolz import curry
from toolz.functoolz import Compose


class pipeable(curry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __rrshift__(self, other):
        """ Use rightshift to represent piping (i.e. `x >> f` is `f(x)`).

        Note that this form of piping assumes a unary function call.
        Use a curried/partial function to allow piping n-ary functions."""
        return self.__call__(other)


    def __rshift__(self, other):
        """ Use rightshift to represent piping (i.e. `x >> f` is `f(x)`).

        Note that this form of piping assumes a unary function call.
        Use a curried/partial function to allow piping n-ary functions."""
        assert callable(other), "All subsequent elements of a pipe must be callable"
        return other.__call__(self)