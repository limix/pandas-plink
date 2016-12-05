from numpy import zeros
from tqdm import tqdm

from _bed_reader import ffi, lib

@ffi.def_extern()
def cb_iter(it, nit, pb):
    print(it)
    ffi.from_handle(pb).update(it)


def read_bed(filepath, nrows, ncols):
    X = zeros((nrows, ncols), int)

    ptr = ffi.cast("uint64_t *", X.ctypes.data)

    nit = 100 if nrows > 100 else nrows

    with tqdm(total=nit) as pb:
        pb = ffi.new_handle(pb)
        lib.read_bed(filepath, nrows, ncols, ptr, nit, lib.cb_iter, pb)

    return X
