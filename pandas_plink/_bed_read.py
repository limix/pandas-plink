from numpy import nan, zeros

from _bed_reader import ffi, lib


def read_bed(filepath, nrows, ncols):
    X = zeros((nrows, ncols), int)
    ptr = ffi.cast("uint64_t *", X.ctypes.data)

    lib.read_bed(filepath, nrows, ncols, ptr)

    X = X.astype(float, copy=False)
    X[X == 3] = nan

    return X
