from math import floor
from pathlib import Path

import dask.array as da
from numpy import ascontiguousarray, empty, float32, float64, nan_to_num, uint8, uint64
from tqdm import tqdm
from xarray import DataArray

__all__ = ["write_bed"]


def write_bed(filepath: Path, X: DataArray, major: str, verbose: bool):
    """
    Write BED file.

    It assumes that ``X`` is a sample-by-variant matrix.
    """
    from .bed_reader import lib

    G = da.asanyarray(X)

    if major == "variant":
        G = G.T

    major_code = 1 if major == "variant" else 0
    e = lib.write_bed_header(str(filepath).encode(), major_code)
    if e != 0:
        raise RuntimeError(f"Failure while writing BED file {filepath}.")

    nrows = G.shape[0]
    ncols = G.shape[1]

    row_chunk = max(1, floor((1024 * 1024 * 256) / ncols))
    row_chunk = min(row_chunk, nrows)

    G = G.rechunk((row_chunk, ncols))

    row_start = 0
    for chunk in tqdm(G.chunks[0], "Writing BED", disable=not verbose):
        data = G[row_start : row_start + chunk, :].compute()
        if data.dtype not in [float32, float64]:
            msg = "Unsupported data type. "
            msg += "Please, provide a dosage matrix in either "
            msg += "float32 or float64 format."
            raise ValueError(msg)

        _write_bed_chunk(filepath, data)
        row_start += chunk


def _write_bed_chunk(filepath: Path, X):
    from .bed_reader import ffi, lib

    base_type = uint8
    base_size = base_type().nbytes
    base_repr = "uint8_t"

    nan_to_num(X, False, 3.0)
    G = ascontiguousarray(X, base_type)
    assert G.flags.aligned

    strides = empty(2, uint64)
    strides[:] = G.strides
    strides //= base_size

    e = lib.write_bed_chunk(
        str(filepath).encode(),
        G.shape[1],
        G.shape[0],
        ffi.cast(f"{base_repr} *", G.ctypes.data),
        ffi.cast("uint64_t *", strides.ctypes.data),
    )
    if e != 0:
        raise RuntimeError(f"Failure while writing BED file {filepath}.")
