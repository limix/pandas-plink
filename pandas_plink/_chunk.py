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
        number of samples. Set to :const:`None` to include all samples.
        Default to :const:`1024`.
    nvariants
        Number of variants in a single chunk, thresholded by the total
        number of variants. Set to :const:`None` to include all variants.
        Default to :const:`1024`.

    Note
    ----
    Small chunks might increase computation time while large chunks
    might increase IO usage. If you have a small data set, try setting
    both :data:`nsamples` and :data:`nvariants` to :const:`None`. If the data set
    is too large but your application will use every sample, try to set
    :data:`nsamples = None` and choose a small value for :data:`nvariants`.

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
