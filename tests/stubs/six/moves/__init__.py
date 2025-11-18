import pickle
from . import queue as queue

cPickle = pickle
_builtin_range = range
range = _builtin_range

__all__ = ['queue', 'cPickle', 'range']
