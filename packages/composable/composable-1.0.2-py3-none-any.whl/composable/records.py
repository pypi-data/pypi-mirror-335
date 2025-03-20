from composable import pipeable
from types import SimpleNamespace
from toolz import get as toolz_get
from functools import reduce as base_reduce

class Record(SimpleNamespace):
    def __init__(self, /, *args, **kwargs):
        assert all(name not in kwargs for name in ('keys', 'values', 'items')), "Record reserves the attributes: keys, values, and items"
        super().__init__(*args, **kwargs)

    def __repr__(self):
        ns_repr = super().__repr__()
        return ns_repr.replace('namespace', 'record')

    def __getitem__(self, key):
        return self.__dict__[key]

    def __or__(self, other):
        assert isinstance(other, dict) or isinstance(other, Record)
        other_dict = other if isinstance(other, dict) else other.__dict__
        out_dict = self.__dict__ | other_dict
        return Record(**out_dict)

    def __ror__(self, other):
        assert isinstance(other, dict) or isinstance(other, Record)
        other_dict = other if isinstance(other, dict) else other.__dict__
        out_dict = other_dict | self.__dict__
        return Record(**out_dict)
        
    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

_maybe_return_record = lambda input_val, out_dict: Record(**out_dict) if isinstance(input_val, Record) else out_dict   

@pipeable
def create(val, *, use_record_class = True, **funcs):
    """ Creates a record by applying keyword functions to the incoming value.

    Args.
        - record: A record (`dict` or `Record`)
        - use_record_class: Whether the output should use the `Record` class
                            [default = True]
        - funcs: One or more functions assigned using keywords.

    Returns.  Creates a record (`Record` or `dict`) by applying each 
              function to the incoming `val` and assigning the result to
              the corresponding key.
    """
    out_dict = {k:f(val) for k, f in funcs.items()}
    return Record(**out_dict) if use_record_class else out_dict   


@pipeable
def apply(record, **funcs):
    """ Apply funcs to the values of the corresponding key.

    Args.
        - record: A record (`dict` or `Record`)
        - funcs: One or more functions assigned using keywords.

    Notes.
        - Apply only acts on the corresponding (existing) value associated
          with the key.
        - key:func pairs will be ignored for any key that isn't in the original record.
        - See `records.update` for a function that gets the whole record as input.

    Returns.  A record of the same type as the argument
              with the values of each keyword updated the
              associated function

    """
    out_dict = {k:funcs[k](val) if k in funcs else val
                    for k, val in record.items()}
    return _maybe_return_record(record, out_dict)

@pipeable
def map(func, record):
    """ Maps `func` to all values of a record.

    Args.
        - func: An arity 1 function
        - record: A record (`dict` or `Record`)

    Returns.  A record of the same type as the argument
              with the value updated using `func`

    """
    out_dict = {k:func(val) for k, val in record.items()}
    return _maybe_return_record(record, out_dict)


@pipeable
def update(record, *, sequential = False, **funcs):
    """ Updates the record by applying each function to the whole record
   and saving the resulting key/value pair.

    Args.
        - record: A record (`dict` or `Record`)
        - sequential: If True, the functions will be applied using the
                      argument order, with each subsequent function getting the 
                      previous resulting value.  This means that value from the previous step
                      can reference the previous keys. [default = False]
        - funcs: One or more functions assigned using keywords.

    Notes.
        - `records.update` gets the whole record as input.
        - Can be used to update existing or create new key:value pairs.
        - See `records.apply` for a function that only acts on the value of the given key.
        
    Returns.  Creates a record (`Record` or `dict`) by applying each 
              function to the entire incoming `record` and assigning the result to
              the corresponding key.
    """
    if sequential and isinstance(record, dict):
        init = {}
        init.update(record)
        def update_record(acc, pair):
            k, f = pair
            acc.update({k:f(acc)})
            return acc
        return base_reduce(update_record, funcs.items(), init)
    elif sequential:
        update_record = lambda acc, p: acc | {p[0]:p[1](acc)}
        return base_reduce(update_record, funcs.items(), record)
    else:
        updates = {k:f(record) for k, f in funcs.items()}
        return _maybe_return_record(record, record | updates)

@pipeable
def get(keys, record):
    """ Extract the values for the corresponding keys from a record.

    Args.
        - keys: Either a single key (string) or a sequence of keys (e.g., list(strings)).
        - record: A record (`dict` or `Record`)

    Returns.  The value or list of values for the corresponding key or keys.
    """
    if isinstance(keys, str):
        return getattr(record, keys) if isinstance(record, Record) else record[keys]
    else:
        return [val for k, val in record.items() if k in keys]

@pipeable
def subset(keys, record):
    """ Create a new record for a subset of the existing keys.

    Args.
        - keys: A sequence of keys (e.g., list(strings)).
        - record: A record (`dict` or `Record`)

    Returns.  Creates a record (`Record` or `dict`) consisting of the
              key/value pairs for the provided `keys`
    """
    out = {k:v for k, v in record.items() if k in keys}
    return _maybe_return_record(record, out)

@pipeable
def zip(record_seq, *, keys = "union", default = None):
    """ Converts a list of records to a record of list containing the original values.

    Args.
        - record_seq: A ordered sequence of records.
        - keys: How to combine the keys, either 
            - `"union"` [default] which uses all keys across all records,
            - `"intersection"` which only uses the keys common to all records, or
            - a list of keys.  Note: The first two options require two passes through the record_seq,
              use the option with record_seq is a single-pass generator/iterator.
        - default: The default value used as a value for any missing key. [default = `None`]

    Returns: A single record of lists.
    """
    if keys == "union":
        init = set([])
        update = lambda acc, r: acc.union(r.keys())
        keys = base_reduce(update, record_seq, init)
    elif keys == "intersection":
        update = lambda acc, r: acc.intersection(r.keys())
        keys = base_reduce(update, record_seq)
    return {k:[toolz_get(k, rec, default = default)
               for rec in record_seq]
            for k in keys
           }

@pipeable
def zip_at(keys, record_seq, *, default = None):
    """ Zip up the values for a list of keys into a single record.

    Args.
        - keys: A list of keys to be zipped.
        - record_seq: A list/tuple of records.
        - default: Value used for any record with a missing key [Default: None]

    Returns. A single dict of key/lists pairs, with the lists containing the original record values.
    """
    return { key: [toolz_get(key, rec, default) for rec in record_seq]
             for key in keys
           }

@pipeable
def heads(n, record):
    """ Applies returns a record after replacing all `list`s or `tuple`s with its head (first n items).

    Args.
        - n: Number of items in the head.
        - record: A record (tuple or Record)

    Note.  This function is useful when inspecting record output containing long lists.
        > (range(1000000)
           >> record.create(x = identity,
                     sqr = lambda x: x**2,
                     is_odd = lambda x: x % 2 == 1
                    )
          ) >> record.heads(2)
           

    Returns.  A record (`Record` or `dict`) with
                 - Any list/tuple value replaced with the head.
                 - All other value left unchanged.
    """
    out = {k: (val[:n]  if isinstance(val, list) or isinstance(val, tuple) else val)
            for k, val in record.items()}
    return _maybe_return_record(record, out)




@pipeable
def group_by(group_by, recs, *, default = None):
    """ Groups records by one or more keys.

    Args.
        - group_by: A single key or a list of keys.
        - recs: A list of records.
        - default: Key to use for any missing groups [default: None]

    Returns: A `dict` of records, with the keys being the unique groups (sting or tuples).
    """
    @pipeable
    def update(group, acc, rec):
        out = acc | {(lbl := toolz_get(group, rec, default)): toolz_get(lbl, acc) + [rec] if lbl in acc else [rec]}
        return out
    return base_reduce(update(group_by), recs, {})

@pipeable
def readable_output(record, *, num_keys = 3, max_len_seq = 3):
    """ Make a more more readable output for a record by trimming the contents to specified limits.
    """
    keys = list(record.keys())[:num_keys]
    return (record
            >> subset(keys)
            >> heads(max_len_seq)
           )