from numpy import float64, int32
from pandas import StringDtype

__all__ = ["bim", "fam"]

bim = {
    "chrom": StringDtype(),
    "snp": StringDtype(),
    "cm": float64,
    "pos": int32,
    "a0": StringDtype(),
    "a1": StringDtype(),
}

fam = {
    "fid": StringDtype(),
    "iid": StringDtype(),
    "father": StringDtype(),
    "mother": StringDtype(),
    "gender": StringDtype(),
    "trait": StringDtype(),
}
