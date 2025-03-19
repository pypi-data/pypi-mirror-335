from .pipeable import pipeable
import re


@pipeable
def split(sep, s):
    ''' splits s into a list of substrings based on sep. analogous to s.split(sep)
    
    args:
        sep: a string used to determine the splitting locations.
        s: the string being splits

    return:
        a list of strings, resulting from splitting s at each instance of sep.
        note that sep is removed in the process.
    '''
    return s.split(sep)


def split_re(pat):
    ''' creates a pipeable function that will split a string using a regular expression based on pat.
    
    args:
        pat: a regular expression pattern used to split strings.

    return:
        a list of strings, resulting from splitting s at each instance of sep.
        note that sep is removed in the process.

    notes:
        Call: 
            To provide efficient computation, split_re returns a pipeable function.
            To perform a regular call: split_re(pat)(s) 
            Use regular syntax for piping: or s >> split_re(pat)

        Partial application: 
            Is curried and can be combined with curried functions (i.e. map)
            Example: list_of_str >> composable.strict.map(split_re("(,|\t)"))
    '''
    r = re.compile(pat)
    return pipeable(lambda s: r.split(s))

@pipeable
def replace(old, new, s, count=-1):
    ''' Return a copy with all occurrences of substring old replaced by new.
    
    args:
        old: substring to be replaced
        new: substring to replacing old
        count: Maximum number of occurrences to replace.
            -1 (the default value) means replace all occurrences.
            If the optional argument count is given, only the first count occurrences are
            replaced.

    returns: a string
    '''
    if count != -1:
        return s.replace(old, new, count)
    else:
        return s.replace(old, new)

@pipeable
def startswith(prefix, S, *, start = None, end = None):
    '''Return True if S starts with the specified prefix, False otherwise.

       With optional start, test S beginning at that position.
       With optional end, stop comparing S at that position.
       prefix can also be a tuple of strings to try.

       Args:
            - prefix - pattern to check for
            - S - String to be checked
            - start - optional index for starting the search
            - end - option end index
    '''
    if start and end:
        return S.startswith(prefix, start, end)
    elif end:
        raise TypeError('Cannot specify an end without also specifying start')
    elif start:
        return S.startswith(prefix, start)
    else:   
        return S.startswith(prefix)


@pipeable
def join(sep, seq):
    ''' Concatenate any number of strings.
    
    The string whose method is called is inserted in between each given string.
    The result is returned as a new string.
    
    Example: 

    >>> from composable.string import join
    >>> ['ab', 'pq', 'rs'] >> join('.')
    'ab.pq.rs'
    '''
    return sep.join(seq)
