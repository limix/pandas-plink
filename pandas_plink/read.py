from __future__ import unicode_literals
from __future__ import division

from collections import OrderedDict as odict
from .bed_reader import read_bed
import pandas as pd

def read_plink(file_prefix):

    fn = {s:"%s.%s" % (file_prefix, s) for s in ['bed', 'bim', 'fam']}

    bim = _read_bim(fn['bim'])
    nmarkers = bim.shape[0]

    fam = _read_fam(fn['fam'])
    nsamples = fam.shape[0]

    bed = _read_bed(fn['bed'], nsamples, nmarkers)

    return (bim, fam, bed)

def _read_bim(fn):
    header = odict([('chrom', 'category'), ('snp', bytes), ('cm', float),
                    ('pos', int), ('a0', 'category'), ('a1', 'category')])
    df = pd.read_csv(fn, delim_whitespace=True, header=None,
                      names=header.keys(),
                      dtype=header,
                      compression=None, index_col=['chrom', 'pos'],
                      engine='c')

    df.sort_index(inplace=True)
    return df

def _read_fam(fn):
    header = odict([('fid', str), ('iid', str), ('father', str),
                    ('mother', str), ('gender', 'category'), ('trait', str)])

    df = pd.read_csv(fn, delim_whitespace=True, header=None,
                     names=header.keys(),
                     dtype=header,
                     compression=None,
                     index_col=['fid', 'iid'],
                     engine='c')

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
    import pdb; pdb.set_trace()
    with open(fn, "rb") as f:
        arr = f.read(2)
        ok = arr[0] == 108 and arr[1] == 27
        if not ok:
            raise ValueError("Invalid BED file: %s." % fn)

def _major_order(fn):
    with open(fn, "rb") as f:
        f.seek(2)
        arr = f.read(1)
        if arr[0] == 1:
            return 'snp'
        elif arr[0] == 0:
            return 'individual'
        raise ValueError("Couldn't understand matrix layout.")

def _ascii_airlock(v):
    if not isinstance(v, bytes):
        v = v.encode()
    return v
