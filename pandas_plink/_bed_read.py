from numpy import absolute, ascontiguousarray, empty, float32, nan, uint8, uint64, zeros

from ._allele import Allele

__all__ = ["read_bed"]


def read_bed(filepath, nrows, ncols, ref: Allele):
    from dask.array import concatenate, from_delayed
    from dask.delayed import delayed

    chunk_size = 1024

    row_start = 0
    col_xs = []
    while row_start < nrows:
        row_end = min(row_start + chunk_size, nrows)
        col_start = 0
        row_xs = []
        while col_start < ncols:
            col_end = min(col_start + chunk_size, ncols)

            x = delayed(_read_bed_chunk)(
                filepath,
                nrows,
                ncols,
                row_start,
                row_end,
                col_start,
                col_end,
                ref,
            )

            shape = (row_end - row_start, col_end - col_start)
            row_xs += [from_delayed(x, shape, float32)]
            col_start = col_end
        col_xs += [concatenate(row_xs, axis=1)]
        row_start = row_end
    X = concatenate(col_xs, axis=0)
    return X


_base_type = uint8
_base_size = _base_type().nbytes
_base_repr = "uint8_t"


def _read_bed_chunk(
    filepath, nrows, ncols, row_start, row_end, col_start, col_end, ref: Allele
):
    from .bed_reader import ffi, lib

    X = zeros((row_end - row_start, col_end - col_start), _base_type)
    assert X.flags.aligned

    strides = empty(2, uint64)
    strides[:] = X.strides
    strides //= _base_size

    e = lib.read_bed_chunk(
        filepath.encode(),
        nrows,
        ncols,
        row_start,
        col_start,
        row_end,
        col_end,
        ffi.cast(f"{_base_repr} *", X.ctypes.data),
        ffi.cast("uint64_t *", strides.ctypes.data),
    )
    if e != 0:
        raise RuntimeError("Failure while reading BED file %s." % filepath)

    X = ascontiguousarray(X, float32)
    X[X == 3] = nan
    if ref == Allele.a0:
        X -= 2
        absolute(X, out=X)

    return X
