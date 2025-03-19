from .compile import *
from traceback import print_exc as _print_exc

def readiter(fp):
    p = fp.readline()
    while p:
        yield p
        p = fp.readline()

class main:
    __slots__ = ('__do_while_condition', )
    
    def __new__(cls, *argv, _a = a):
        return super().__new__(cls).__init__(argv) if len(argv) else main(*_a)
    
    def __init__(self, argv):
        self.__do_while_condition = True
        self(*argv)

    def __call__(self, thisfile, *argv):
        L = len(argv)
        if L:
            self.__runfile(*argv)
        else:
            while self.__do_while_condition:
                cmd = input('$ ')
                self.__do_while_condition = (cmd != 'exit')
                runlinef(cmd)()
    
    def __runfile(self, file):
        with open(file) as fp:
            for f in map(runlinef, map(ignorlast, readiter(fp))):
                f()

if __name__ == "__main__" : main()