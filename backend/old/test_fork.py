import os
import sys

class C:
    def __init__(self):
        print('Constructor')

    def __del__(self):
        print('Destructor')

def f():
    obj = C()
    os.fork()

f()
