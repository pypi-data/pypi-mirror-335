class PipeableObject(object):
    def __init__(self, function = lambda x: x, after_method_call = False):
        self._function = function
        self._after_method_call = after_method_call

    def __getattr__(self, name):
        return PipeableObject(lambda x: getattr(self._function(x), name), after_method_call = False)

    def __call__(self, *args, **kwargs):
        if self._after_method_call:
            return self._function(*args, **kwargs)
        else:
            return PipeableObject(lambda x: self._function(x)(*args, **kwargs),
                                  after_method_call = True)

    def __rrshift__(self, other):
        return self._function(other)

obj = PipeableObject()

class PipeableAttribute(object):
    def __init__(self, function = lambda x: x):
        self.function = function

    def __getattr__(self, name):
        return pipeable(lambda x: getattr(x, name))
    
    def __rrshift__(self, other):
        return self.function(other)
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

attr = PipeableAttribute()