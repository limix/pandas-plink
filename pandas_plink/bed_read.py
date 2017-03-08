import dask.array as da
from dask.array import from_delayed
from dask.delayed import delayed
from numpy import int64, zeros

from .bed_reader import ffi, lib


def read_bed_chunk(filepath, nrows, ncols, row_start, row_end, col_start,
                   col_end):

    X = zeros((row_end - row_start, col_end - col_start), int64)

    ptr = ffi.cast("uint64_t *", X.ctypes.data)

    e = lib.read_bed_chunk(filepath, nrows, ncols, row_start, col_start,
                           row_end, col_end, ptr)
    if e != 0:
        raise RuntimeError("Failure while reading BED file %s." % filepath)

    return X


def read_bed(filepath, nrows, ncols):
    chunk_bytes = 256

    row_start = 0
    col_xs = []
    while (row_start < nrows):
        row_end = min(row_start + chunk_bytes * 4, nrows)
        col_start = 0
        row_xs = []
        while (col_start < ncols):
            col_end = min(col_start + chunk_bytes * 4, ncols)

            x = delayed(read_bed_chunk)(filepath, nrows, ncols, row_start,
                                        row_end, col_start, col_end)

            shape = (row_end - row_start, col_end - col_start)
            row_xs += [from_delayed(x, shape, int64)]
            col_start = col_end
        col_xs += [da.concatenate(row_xs, axis=1)]
        row_start = row_end
    X = da.concatenate(col_xs, axis=0)
    return X
