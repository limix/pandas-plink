from numpy import zeros
from tqdm import tqdm

from _bed_reader import ffi, lib

@ffi.def_extern()
def cb_iter(pb):
    ffi.from_handle(pb).update(1)


def read_bed(filepath, nrows, ncols, verbose):
    X = zeros((nrows, ncols), int)

    ptr = ffi.cast("uint64_t *", X.ctypes.data)

    nit = 100 if nrows > 100 else nrows

    with tqdm(total=nit, disable=not verbose) as pb0:
        pb = ffi.new_handle(pb0)
        e = lib.read_bed(filepath, nrows, ncols, ptr, nit, lib.cb_iter, pb)
        if e != 0:
            raise RuntimeError("Failure while reading BED file %s." % filepath)

    return X

def read_bed_chunk(filepath, nrows, ncols, row_start, row_end, col_start,
                   col_end):

    X = zeros((row_end - row_start, col_end - col_start), int)

    ptr = ffi.cast("uint64_t *", X.ctypes.data)

    e = lib.read_bed_chunk(filepath, nrows, ncols, row_start, col_start,
                           row_end, col_end, ptr)
    if e != 0:
        raise RuntimeError("Failure while reading BED file %s." % filepath)

    return X
