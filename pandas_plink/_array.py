import numpy as np
import dask.array as da
from dask.delayed import delayed

from dask.array import from_delayed

if __name__ == '__main__':
    def read(name):
        print(name)
        return np.load('%s.npy' % name)

    x00 = from_delayed(delayed(read)('x00'), (5, 2), float)
    x01 = from_delayed(delayed(read)('x01'), (5, 2), float)

    x10 = from_delayed(delayed(read)('x10'), (3, 2), float)
    x11 = from_delayed(delayed(read)('x11'), (3, 2), float)

    row0 = da.hstack((x00, x01))
    row1 = da.hstack((x10, x11))

    X = da.vstack((row0, row1))

    print(X[0,:].compute())
