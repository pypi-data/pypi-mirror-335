from composable import pipeable
from functools import reduce as base_reduce

@pipeable
def fold(update, init, seq):
    """ Folds/reduces a sequence using an update function and initial value.
    """
    return base_reduce(update, seq, init)

@pipeable
def reduce(update, seq):
    """ Folds/reduces a sequence using an update function and default initial value (first element).
    """
    return base_reduce(update, seq)

@pipeable
def unfoldl(empty, func, state):
    """ Decompose a value into parts by unfolds the state to the left.

    Args.
        - empty: A function that takes the current state as input 
                 and returns True when state is empty and the process 
                 should stop and return.
        - func: An arity 2 function that takes the current (non-empty) state
                as input and returns (new, state); e.g., the next component
                new and the updated state.
        - state: The initial state to be decomposed.

    Returns: A list of values representing the decomposed parts of the 
             original state, where the components accumulate to the left
             (thus the "l" in unfoldl)
    """
    out = []
    while not empty(state):
        new, state = func(state)
        out = [new] + out
    return out


@pipeable
def unfoldr(empty, func, state):
    """ Decompose a value into parts by unfolds the state to the right.

    Args.
        - empty: A function that takes the current state as input 
                 and returns True when state is empty and the process 
                 should stop and return.
        - func: An arity 2 function that takes the current (non-empty) state
                as input and returns (new, state); e.g., the next component
                new and the updated state.
        - state: The initial state to be decomposed.

    Returns: A list of values representing the decomposed parts of the 
             original state, where the components accumulate to the right
             (thus the "r" in unfoldr)
    """
    out = []
    while not empty(state):
        new, state = func(state)
        out = out + [new]
    return out

@pipeable
def unfoldl_iter(func, state, seq):
    """ Decompose a sequence into a new sequence by iterating and unfolding 
    to the left using some updating state.

    Args.
        - func: An arity 2 function that takes the current (non-empty) state
                and next val of seq [in that order] 
                and returns (new, state); e.g., the next component `new` 
                and the updated `state`.
                e.g., `new, state = func(state, val)`
        - state: The initial state.
        - seq: A sequence of values, which is iterated through from right 
               to left. Must be reversable.

    Returns: A list of values representing the decomposed parts of the 
             original state and sequence, where the components accumulate 
             from right to left (read the "l" in unfoldl_iter as TO THE 
             LEFT)

    Example
    > add = lambda x, y: (x + y, x + y)
    > cumult_suml = lambda seq: unfoldl_iter(add, 0, seq)
    > cumult_suml([0, 1, 2, 3, 4])
    [1] [10, 10, 9, 7, 4]
    """
    out = []
    for val in reversed(seq):
        new, state = func(state, val)
        out = [new] + out
    return out


@pipeable
def unfoldr_iter(func, state, seq):
    """ Decompose a sequence into a new sequence by iterating and unfolding 
    left to right using some updating state.

    Args.
        - func: An arity 2 function that takes the current (non-empty) state
                and next val of seq [in that order] 
                and returns (new, state); e.g., the next component `new` 
                and the updated `state`.
                e.g., `new, state = func(state, val)`
        - state: The initial state.
        - seq: A sequence of values, which is iterated through from left 
               to right.

    Returns: A list of values representing the decomposed parts of the 
             original state and sequence, where the components accumulate 
             left to right (read the "r" in unfoldr_iter as TO THE RIGHT)

    Example
    > add = lambda x, y: (x + y, x + y)
    > cumult_sumr = lambda seq: unfoldl_iter(add, 0, seq)
    > cumult_sumr([0, 1, 2, 3, 4])
    [1] [0, 1, 3, 6, 10]
    """
    out = []
    for val in seq:
        new, state = func(state, val)
        out = out + [new]
    return out