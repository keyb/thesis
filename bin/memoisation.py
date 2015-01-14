def memoise(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return memodict(f)

# from functools import partial
#
# class memoise(object):
#     """cache the return value of a method
#
#     This class is meant to be used as a decorator of methods. The return value
#     from a given method invocation will be cached on the instance whose method
#     was invoked. All arguments passed to a method decorated with memoize must
#     be hashable.
#
#     If a memoized method is invoked directly on its class the result will not
#     be cached. Instead the method will be invoked like a static method:
#     class Obj(object):
#         @memoize
#         def add_to(self, arg):
#             return self + arg
#     Obj.add_to(1) # not enough arguments
#     Obj.add_to(1, 2) # returns 3, result is not cached
#     """
#     def __init__(self, func):
#         self.func = func
#     def __get__(self, obj, objtype=None):
#         if obj is None:
#             return self.func
#         return partial(self, obj)
#     def __call__(self, *args, **kw):
#         obj = args[0]
#         try:
#             cache = obj.__cache
#         except AttributeError:
#             cache = obj.__cache = {}
#         key = (self.func, args[1:], frozenset(kw.items()))
#         try:
#             res = cache[key]
#         except KeyError:
#             res = cache[key] = self.func(*args, **kw)
#         return res