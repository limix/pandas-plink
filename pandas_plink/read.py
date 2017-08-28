from __future__ import division, unicode_literals

import sys
from collections import OrderedDict as odict
from glob import glob
from os.path import basename, dirname, join

from tqdm import tqdm

from .bed_read import read_bed

PY3 = sys.version_info >= (3, )

if PY3:

    def _ord(x):
        return x
else:
    _ord = ord


def read_plink(file_prefix, verbose=True):
    r"""Read PLINK files into Pandas data frames.

    Parameters
    ----------
    file_prefix : str
        Path prefix to the set of PLINK files. It supports loading many BED
        files at once using globstrings wildcard.
    verbose : bool
        ``True`` for progress information; ``False`` otherwise.

    Returns
    -------
    :class:`pandas.DataFrame`
        Alleles.
    :class:`pandas.DataFrame`
        Samples.
    :class:`numpy.ndarray`
        Genotype.

    Examples
    --------
    We have shipped this package with an example so can load and inspect by
    doing

    .. doctest::

        >>> from pandas_plink import read_plink
        >>> from pandas_plink import example_file_prefix
        >>> (bim, fam, bed) = read_plink(example_file_prefix(), verbose=False)
        >>> print(bim.head()) #doctest: +NORMALIZE_WHITESPACE
          chrom         snp   cm    pos a0 a1  i
        0     1  rs10399749  0.0  45162  G  C  0
        1     1   rs2949420  0.0  45257  C  T  1
        2     1   rs2949421  0.0  45413  0  0  2
        3     1   rs2691310  0.0  46844  A  T  3
        4     1   rs4030303  0.0  72434  0  G  4
        >>> print(fam.head()) #doctest: +NORMALIZE_WHITESPACE
                fid       iid    father    mother gender trait  i
        0  Sample_1  Sample_1         0         0      1    -9  0
        1  Sample_2  Sample_2         0         0      2    -9  1
        2  Sample_3  Sample_3  Sample_1  Sample_2      2    -9  2
        >>> print(bed.compute())
        [[  2.   2.   1.]
         [  2.   1.   2.]
         [ nan  nan  nan]
         [ nan  nan   1.]
         [  2.   2.   2.]
         [  2.   2.   2.]
         [  2.   1.   0.]
         [  2.   2.   2.]
         [  1.   2.   2.]
         [  2.   1.   2.]]

    Notice the `i` column in bim and fam data frames. It maps to the
    corresponding position of the bed matrix:

    .. doctest::

        >>> from pandas_plink import read_plink
        >>> from pandas_plink import example_file_prefix
        >>> (bim, fam, bed) = read_plink(example_file_prefix(), verbose=False)
        >>> chrom1 = bim.query("chrom=='1'")
        >>> X = bed[chrom1.i,:].compute()
        >>> print(X) #doctest: +NORMALIZE_WHITESPACE
        [[  2.   2.   1.]
         [  2.   1.   2.]
         [ nan  nan  nan]
         [ nan  nan   1.]
         [  2.   2.   2.]
         [  2.   2.   2.]
         [  2.   1.   0.]
         [  2.   2.   2.]
         [  1.   2.   2.]
         [  2.   1.   2.]]

    It also allows the use of the wildcard character ``*`` for mapping
    multiple BED files at
    once: ``(bim, fam, bed) = read_plink("chrom*")``.
    In this case, only one of the FAM files will be used to define
    sample information. Data from BIM and BED files are concatenated to
    provide a single view of the files.
    """
    from pandas import concat
    from dask.array import concatenate

    file_prefixes = glob(file_prefix)
    if len(file_prefixes) == 0:
        file_prefixes = [file_prefix.replace('*', '')]

    file_prefixes = _clean_prefixes(file_prefixes)

    fn = []
    for fp in file_prefixes:
        fn.append({s: "%s.%s" % (fp, s) for s in ['bed', 'bim', 'fam']})

    pbar = tqdm(desc="Mapping files", total=3 * len(fn), disable=not verbose)
    bim = _read_file(fn, "Reading bim file(s)...",
                     lambda fn: _read_bim(fn['bim']), pbar)

    nmarkers = dict()
    for i, bi in enumerate(bim):
        nmarkers[fn[i]['bed']] = bi.shape[0]
    bim = concat(bim, axis=0, ignore_index=True)

    fam = _read_file([fn[0]], "Reading fam file(s)...",
                     lambda fn: _read_fam(fn['fam']), pbar)[0]
    nsamples = fam.shape[0]

    bed = _read_file(
        fn, "Reading bed file(s)...",
        lambda fn: _read_bed(fn['bed'], nsamples, nmarkers[fn['bed']]), pbar)

    bed = concatenate(bed, axis=0)

    pbar.close()

    return (bim, fam, bed)


def _read_file(fn, desc, read_func, pbar):
    data = []
    for f in fn:
        data.append(read_func(f))
        pbar.update(1)
    return data


def _read_csv(fn, header):
    from pandas import read_csv

    return read_csv(
        fn,
        delim_whitespace=True,
        header=None,
        names=header.keys(),
        dtype=header,
        compression=None,
        engine='c')


def _read_bim(fn):
    header = odict([('chrom', bytes), ('snp', bytes), ('cm', float),
                    ('pos', int), ('a0', bytes), ('a1', bytes)])
    df = _read_csv(fn, header)

    df['chrom'] = df['chrom'].astype('category')
    df['a0'] = df['a0'].astype('category')
    df['a1'] = df['a1'].astype('category')
    df['i'] = range(df.shape[0])
    return df


def _read_fam(fn):
    header = odict([('fid', str), ('iid', str), ('father', str),
                    ('mother', str), ('gender', bytes), ('trait', str)])

    df = _read_csv(fn, header)

    df['gender'] = df['gender'].astype('category')
    df['i'] = range(df.shape[0])
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
        if len(arr) < 2:
            raise ValueError("Couldn't read BED header: %s." % fn)
        ok = _ord(arr[0]) == 108 and _ord(arr[1]) == 27
        if not ok:
            raise ValueError("Invalid BED file: %s." % fn)


def _major_order(fn):
    with open(fn, "rb") as f:
        f.seek(2)
        arr = f.read(1)
        if len(arr) < 1:
            raise ValueError("Couldn't read column order: %s." % fn)
        if _ord(arr[0]) == 1:
            return 'snp'
        elif _ord(arr[0]) == 0:
            return 'individual'
        raise ValueError("Couldn't understand matrix layout.")


def _ascii_airlock(v):
    if not isinstance(v, bytes):
        v = v.encode()
    return v


def _clean_prefixes(prefixes):
    paths = []
    for p in prefixes:
        dirn = dirname(p)
        basen = basename(p)
        base = '.'.join(basen.split('.')[:-1])
        if len(base) == 0:
            path = p
        else:
            ext = basen.split('.')[-1]
            if ext not in ['bed', 'fam', 'bim']:
                base += '.' + ext
            path = join(dirn, base)
        paths.append(path)
    return list(set(paths))
