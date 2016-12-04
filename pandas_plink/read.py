from __future__ import division, unicode_literals

import sys
from collections import OrderedDict as odict

import pandas as pd

from .bed_reader import read_bed

PY3 = sys.version_info >= (3, )

if PY3:
    _ord = lambda x: x
else:
    _ord = ord



def read_plink(file_prefix):
    r"""Convert PLINK files into Pandas data frames.

    Args:
        file_prefix (str): Path prefix to the set of PLINK files.

    Returns:
        (tuple): parsed data containing:

            * bim (pandas.DataFrame): alleles.
            * fam (pandas.DataFrame): samples.
            * bed (numpy.ndarray): genotype.

    Examples:

        Assume that you have the following files:

        - /path/to/data.bim
        - /path/to/data.fam
        - /path/to/data.bed

        You can simply do

        >>> from pandas_plink import read_plink
        >>> (bim, fam, bed) = read_plink('/path/to/data')

        to parse them into data frames `bim` and `fam` and into
        NumPy array `bed`.
    """

    fn = {s: "%s.%s" % (file_prefix, s) for s in ['bed', 'bim', 'fam']}

    bim = _read_bim(fn['bim'])
    nmarkers = bim.shape[0]

    fam = _read_fam(fn['fam'])
    nsamples = fam.shape[0]

    bed = _read_bed(fn['bed'], nsamples, nmarkers)

    return (bim, fam, bed)


def _read_bim(fn):
    header = odict([('chrom', 'category'), ('snp', bytes), ('cm', float),
                    ('pos', int), ('a0', 'category'), ('a1', 'category')])
    df = pd.read_csv(
        fn,
        delim_whitespace=True,
        header=None,
        names=header.keys(),
        dtype=header,
        compression=None,
        index_col=['chrom', 'pos'],
        engine='c')

    df['i'] = range(df.shape[0])
    df.sort_index(inplace=True)
    return df


def _read_fam(fn):
    header = odict([('fid', str), ('iid', str), ('father', str),
                    ('mother', str), ('gender', 'category'), ('trait', str)])

    df = pd.read_csv(
        fn,
        delim_whitespace=True,
        header=None,
        names=header.keys(),
        dtype=header,
        compression=None,
        index_col=['fid', 'iid'],
        engine='c')

    df['i'] = range(df.shape[0])
    df.sort_index(inplace=True)
    return df


def _read_bed(fn, nsamples, nmarkers):
    fn = _ascii_airlock(fn)

    _check_bed_header(fn)
    major = _major_order(fn)

    ncols = nmarkers if major == 'individual' else nsamples
    nrows = nmarkers if major == 'snp' else nsamples

    return read_bed(fn, nrows, ncols)


def _check_bed_header(fn):
    with open(fn, "rb") as f:
        arr = f.read(2)
        ok = _ord(arr[0]) == 108 and _ord(arr[1]) == 27
        if not ok:
            raise ValueError("Invalid BED file: %s." % fn)


def _major_order(fn):
    with open(fn, "rb") as f:
        f.seek(2)
        arr = f.read(1)
        if _ord(arr[0]) == 1:
            return 'snp'
        elif _ord(arr[0]) == 0:
            return 'individual'
        raise ValueError("Couldn't understand matrix layout.")


def _ascii_airlock(v):
    if not isinstance(v, bytes):
        v = v.encode()
    return v
