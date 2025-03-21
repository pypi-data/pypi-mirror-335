from composable import pipeable

#
### Tentative tuple class based on namedtuples
#
# from collections import namedtuple
# tuple_names = lambda n, *, prefix = 'i': [f"{prefix}{i}" for i in range(n)]
# 
# tuple_names(5)
# 
# make_tuple = lambda seq, *, name = 'Tuple', prefix = 'i': namedtuple(f"{name}{len(seq)}", tuple_names(len(seq), prefix = prefix))(*seq)
# 
# (tup := make_tuple(range(5)))
# 
# tup.i1

@pipeable
def create_tuple(funcs, val):
    return tuple(f(val) for f in funcs)
    
@pipeable
def apply(funcs, tup):
    return tuple(f(val) for f, val in zip(funcs, tup))
    
@pipeable
def apply_by_index(index_dict, tup):
    return tuple(index_dict[i](val) if i in index_dict else val
                 for i, val in enumerate(tup))

@pipeable
def map(func, tup):
    return tuple(func(val) for val in tup)

@pipeable
def with_(preds, tup, /, all_ = True):
    truth = tuple(p(f) for p, f in zip(preds, tup))
    if all_:
        return all(truth)
    else:
        return any(truth)

@pipeable
def with_index(pred_dict, tup, /, all_ = True):
    truth = [pred_dict[i](val) for i, val in enumerate(tup) if i in pred_dict]
    if all_:
        return all(truth)
    else:
        return any(truth)

@pipeable
def head(n, tup):
    """ Returns the head of a tuple/list (for `n` elements).

    Args:
        - n: Number of items in the head
        - tup: a list or tuple

    Returns: The head of `tup`
    """
    return tup[:n]

@pipeable
def first(tup):
    """ Returns the first element of a tuple/list.
    """
    return tup[0]

@pipeable
def rest(tup):
    """ Returns all but the first element of a tuple/list
    """
    return tup[1:]