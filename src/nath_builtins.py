import math, time
from collections import namedtuple

Func = namedtuple("Func", ['name', 'arity'])

functions = [
    Func("cos", 1), 
    Func("sin", 1), 
    Func("now", 0)
]

def _sin(x): 
    return math.sin(x)
def _cos(x): 
    return math.cos(x)
def _now():
    return time.time()