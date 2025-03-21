from .pipeable import pipeable
import operator as op


is_lt = pipeable(lambda b, a: op.lt(a, b))
is_le = pipeable(lambda b, a: op.le(a, b))
is_eq = pipeable(lambda b, a: op.eq(a, b))
is_ne = pipeable(lambda b, a: op.ne(a, b))
is_ge = pipeable(lambda b, a: op.ge(a, b))
is_gt = pipeable(lambda b, a: op.gt(a, b))


not_ = pipeable(lambda obj:    op.not_(obj))
truth = pipeable(lambda obj:   op.truth(obj))
is_ = pipeable(lambda a, b:    op.is_(a, b))
is_not = pipeable(lambda a, b: op.is_not(a, b))
