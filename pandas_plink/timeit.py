import sys
from time import time

class TimeIt(object):
    def __init__(self, msg, silent=False):
        self._msg = msg
        self._start = None
        self._silent = silent

    def __enter__(self):
        if self._silent:
            return
        self._start = time()
        sys.stdout.write(self._msg)
        sys.stdout.flush()

    def __exit__(self, *args):
        if self._silent:
            return
        elapsed = time() - self._start
        print(' done (%.2f s)' % (elapsed,))
        sys.stdout.flush()
