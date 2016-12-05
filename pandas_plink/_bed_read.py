from numpy import nan, zeros

from _bed_reader import ffi, lib

@ffi.def_extern()
def cb_iter():
    pass


def read_bed(filepath, nrows, ncols):
    import sys
    print("ponto 0.1");sys.stdout.flush()
    X = zeros((nrows, ncols), int)

    print("ponto 0.2");sys.stdout.flush()
    ptr = ffi.cast("uint64_t *", X.ctypes.data)

    print("ponto 0.3");sys.stdout.flush()
    lib.read_bed(filepath, nrows, ncols, ptr, 10, lib.cb_iter)
    # lib.read_bed(filepath, nrows, ncols, ptr)

    print("ponto 0.4");sys.stdout.flush()
    X = X.astype(float, copy=False)
    print("ponto 0.5");sys.stdout.flush()
    X[X == 3] = nan
    print("ponto 0.6");sys.stdout.flush()

    return X
