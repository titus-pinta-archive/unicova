import os
import sys
from contextlib import contextmanager

class C:
    def __init__(self):
        print('Constructor')

    def __del__(self):
        print('Destructor')

@contextmanager
def cm():
    print('Context manager')
    yield True
    print('Exit')

def f():
    #obj = C()
    #os.fork()
    #raise ValueError('error')
    with cm:
        print('Inside')

f()
