from dataclasses import dataclass
from typing import Optional

__all__ = ["Chunk"]


@dataclass
class Chunk:
    """
    Chunk specification.

    It is effectively a contiguous submatrix of the dosage matrix.

    Parameters
    ----------
    nsamples
        Number of samples in a single chunk, thresholded by the total
        number of samples. Set to ``None`` to include all samples.
        Default to ``1024``.
    nvariants
        Number of variants in a single chunk, thresholded by the total
        number of variants. Set to ``None`` to include all variants.
        Default to ``1024``.

    Note
    ----
    Small chunks might increase computation time while large chunks
    might increase IO usage. If you have a small data set, try setting
    both ``nsamples`` and ``nvariants`` to ``None``. If the data set
    is too large but your application will use every sample, try to set
    ``nsamples=None`` and choose a small value for ``nvariants``.

    Examples
    --------
    .. doctest::

        >>> from pandas_plink import Chunk
        >>>
        >>> Chunk()
        Chunk(nsamples=1024, nvariants=1024)
        >>> Chunk(nsamples=None)
        Chunk(nsamples=None, nvariants=1024)
    """

    nsamples: Optional[int] = 1024
    nvariants: Optional[int] = 1024
