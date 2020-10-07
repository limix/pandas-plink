import warnings
from collections import OrderedDict as odict
from glob import glob
from os.path import basename, dirname, join

from deprecated.sphinx import deprecated

from ._allele import Allele
from ._bed_read import read_bed
from ._chunk import Chunk
from ._util import last_replace

__all__ = ["read_plink", "read_plink1_bin"]


@deprecated(reason="use function :func:`read_plink1_bin` instead.", version="2.1.0")
def read_plink(file_prefix, verbose=True):
    """
    Read PLINK files into data frames.

    Examples
    --------
    We have shipped this package with an example so can load and inspect by doing

    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_plink
        >>> from pandas_plink import get_data_folder
        >>> (bim, fam, bed) = read_plink(join(get_data_folder(), "data"), verbose=False)
        >>> print(bim.head())
          chrom         snp       cm    pos a0 a1  i
        0     1  rs10399749     0.00  45162  G  C  0
        1     1   rs2949420     0.00  45257  C  T  1
        2     1   rs2949421     0.00  45413  0  0  2
        3     1   rs2691310     0.00  46844  A  T  3
        4     1   rs4030303     0.00  72434  0  G  4
        >>> print(fam.head())
                fid       iid    father    mother gender trait  i
        0  Sample_1  Sample_1         0         0      1    -9  0
        1  Sample_2  Sample_2         0         0      2    -9  1
        2  Sample_3  Sample_3  Sample_1  Sample_2      2    -9  2
        >>> print(bed.compute())
        [[2.00 2.00 1.00]
         [2.00 1.00 2.00]
         [ nan  nan  nan]
         [ nan  nan 1.00]
         [2.00 2.00 2.00]
         [2.00 2.00 2.00]
         [2.00 1.00 0.00]
         [2.00 2.00 2.00]
         [1.00 2.00 2.00]
         [2.00 1.00 2.00]]

    The values of the ``bed`` matrix denote how many alleles ``a1`` (see output of data
    frame ``bim``) are in the corresponding position and individual. Notice the column
    ``i`` in ``bim`` and ``fam`` data frames. It maps to the corresponding position of
    the bed matrix:

    .. doctest::

        >>> chrom1 = bim.query("chrom=='1'")
        >>> X = bed[chrom1.i.values, :].compute()
        >>> print(X)
        [[2.00 2.00 1.00]
         [2.00 1.00 2.00]
         [ nan  nan  nan]
         [ nan  nan 1.00]
         [2.00 2.00 2.00]
         [2.00 2.00 2.00]
         [2.00 1.00 0.00]
         [2.00 2.00 2.00]
         [1.00 2.00 2.00]
         [2.00 1.00 2.00]]

    It also allows the use of the wildcard character ``*`` for mapping
    multiple BED files at
    once: ``(bim, fam, bed) = read_plink("chrom*")``.
    In this case, only one of the FAM files will be used to define
    sample information. Data from BIM and BED files are concatenated to
    provide a single view of the files.

    Parameters
    ----------
    file_prefix : str
        Path prefix to the set of PLINK files. It supports loading many BED files at
        once using globstrings wildcard.
    verbose : bool
        ``True`` for progress information; ``False`` otherwise.

    Returns
    -------
    alleles : :class:`pandas.DataFrame`
        Alleles.
    samples : :class:`pandas.DataFrame`
        Samples.
    genotypes : :class:`numpy.ndarray`
        Genotype.
    """
    import pandas as pd
    from dask.array import concatenate
    from tqdm import tqdm

    file_prefixes = sorted(glob(file_prefix))
    if len(file_prefixes) == 0:
        file_prefixes = [file_prefix.replace("*", "")]

    file_prefixes = sorted(_clean_prefixes(file_prefixes))

    fn = []
    for fp in file_prefixes:
        fn.append({s: "%s.%s" % (fp, s) for s in ["bed", "bim", "fam"]})

    pbar = tqdm(desc="Mapping files", total=3 * len(fn), disable=not verbose)

    bim = _read_file(fn, lambda fn: _read_bim(fn["bim"]), pbar)
    if len(file_prefixes) > 1:
        if verbose:
            msg = "Multiple files read in this order: {}"
            print(msg.format([basename(f) for f in file_prefixes]))

    nmarkers = dict()
    index_offset = 0
    for i, bi in enumerate(bim):
        nmarkers[fn[i]["bed"]] = bi.shape[0]
        bi["i"] += index_offset
        index_offset += bi.shape[0]
    bim = pd.concat(bim, axis=0, ignore_index=True)

    fam = _read_file([fn[0]], lambda fn: _read_fam(fn["fam"]), pbar)[0]
    nsamples = fam.shape[0]

    ref = Allele.a1
    bed = _read_file(
        fn,
        lambda f: _read_bed(f["bed"], nsamples, nmarkers[f["bed"]], ref, Chunk()),
        pbar,
    )

    bed = concatenate(bed, axis=0)

    pbar.close()

    return (bim, fam, bed)


def read_plink1_bin(
    bed, bim=None, fam=None, verbose=True, ref="a1", chunk: Chunk = Chunk()
):
    """
    Read PLINK 1 binary files [1]_ into a data array.

    A PLINK 1 binary file set consists of three files:

    - BED: containing the genotype.
    - BIM: containing variant information.
    - FAM: containing sample information.

    The user might provide a single file path to a BED file, from which this function
    will try to infer the file path of the other two files.
    This function also allows the user to provide file path to multiple BED and
    BIM files, as it is common to have a data set split into multiple files, one per
    chromosome.

    This function returns a samples-by-variants matrix. This is a special kind of matrix
    with rows and columns having multiple coordinates each. Those coordinates have the
    metainformation contained in the BIM and FAM files.

    Examples
    --------
    The following example reads two BED files and two BIM files correspondig to
    chromosomes 11 and 12, and read a single FAM file whose filename is inferred from
    the BED filenames.

    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_plink1_bin
        >>> from pandas_plink import get_data_folder
        >>> G = read_plink1_bin(join(get_data_folder(), "chr*.bed"), verbose=False)
        >>> print(G)
        <xarray.DataArray 'genotype' (sample: 14, variant: 1252)>
        dask.array<concatenate, shape=(14, 1252), dtype=float32, chunksize=(14, 779), chunktype=numpy.ndarray>
        Coordinates:
          * sample   (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
          * variant  (variant) object '11_316849996' '11_316874359' ... '12_373081507'
            fid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            iid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            father   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            mother   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            gender   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            trait    (sample) object '-9' '-9' '-9' '-9' '-9' ... '-9' '-9' '-9' '-9'
            chrom    (variant) object '11' '11' '11' '11' '11' ... '12' '12' '12' '12'
            snp      (variant) object '316849996' '316874359' ... '373081507'
            cm       (variant) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0
            pos      (variant) int32 157439 181802 248969 ... 27163741 27205125 27367844
            a0       (variant) object 'C' 'G' 'G' 'C' 'C' 'T' ... 'A' 'G' 'A' 'T' 'G'
            a1       (variant) object 'T' 'C' 'C' 'T' 'T' 'A' ... 'G' 'A' 'T' 'C' 'A'
        >>> print(G.shape)
        (14, 1252)

    Suppose we want the genotypes of the chromosome 11 only:

    .. doctest::

        >>> G = G.where(G.chrom == "11", drop=True)
        >>> print(G)
        <xarray.DataArray 'genotype' (sample: 14, variant: 779)>
        dask.array<where, shape=(14, 779), dtype=float32, chunksize=(14, 779), chunktype=numpy.ndarray>
        Coordinates:
          * sample   (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
          * variant  (variant) object '11_316849996' '11_316874359' ... '11_345698259'
            fid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            iid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            father   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            mother   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            gender   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            trait    (sample) object '-9' '-9' '-9' '-9' '-9' ... '-9' '-9' '-9' '-9'
            chrom    (variant) object '11' '11' '11' '11' '11' ... '11' '11' '11' '11'
            snp      (variant) object '316849996' '316874359' ... '345698259'
            cm       (variant) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0
            pos      (variant) int32 157439 181802 248969 ... 28937375 28961091 29005702
            a0       (variant) object 'C' 'G' 'G' 'C' 'C' 'T' ... 'A' 'C' 'A' 'A' 'T'
            a1       (variant) object 'T' 'C' 'C' 'T' 'T' 'A' ... 'G' 'T' 'G' 'C' 'C'
        >>> print(G.shape)
        (14, 779)

    Lets now print the genotype value of the sample `B003` for variant `11_316874359`:

    .. doctest::

        >>> print(G.sel(sample="B003", variant="11_316874359").values)
        0.0

    The special matrix we return is of type :class:`xarray.DataArray`. More information
    about it can be found at the `xarray documentation <http://xarray.pydata.org>`_.


    Parameters
    ----------
    bed : str
        Path to a BED file. It can contain shell-style wildcards to indicate multiple
        BED files.
    bim : str, optional
        Path to a BIM file. It can contain shell-style wildcards to indicate multiple
        BIM files. It defaults to ``None``, in which case it will try to be inferred.
    fam : str, optional
        Path to a FAM file. It defaults to ``None``, in which case it will try to be
        inferred.
    verbose : bool
        ``True`` for progress information; ``False`` otherwise.
    ref: str, optional
        Reference allele. Specify which allele the dosage matrix will count. It can
        be either ``"a1"`` (default) or ``"a0"``.

    Returns
    -------
    G : :class:`xarray.DataArray`
        Genotype with metadata.

    References
    ----------
    .. [1] PLINK 1 binary. https://www.cog-genomics.org/plink/2.0/input#bed
    """
    import dask.array as da
    import pandas as pd
    from tqdm import tqdm
    from xarray import DataArray

    bed_files = sorted(glob(bed))
    if len(bed_files) == 0:
        raise ValueError("No BED file has been found.")

    if bim is None:
        bim_files = [last_replace(f, ".bed", ".bim") for f in bed_files]
    else:
        bim_files = sorted(glob(bim))
    if len(bim_files) == 0:
        raise ValueError("No BIM file has been found.")

    if fam is None:
        fam_files = [last_replace(f, ".bed", ".fam") for f in bed_files]
    else:
        fam_files = sorted(glob(fam))
    if len(fam_files) == 0:
        raise ValueError("No FAM file has been found.")

    if len(bed_files) != len(bim_files):
        raise ValueError("The numbers of BED and BIM files must match.")

    if len(fam_files) > 1:
        msg = "More than one FAM file has been specified. Only the first one will be "
        msg += "considered."
        if verbose:
            warnings.warn(msg, UserWarning)
        fam_files = fam_files[:1]

    nfiles = len(bed_files) + len(bim_files) + 1
    pbar = tqdm(desc="Mapping files", total=nfiles, disable=not verbose)

    bims = _read_file(bim_files, lambda f: _read_bim(f), pbar)
    nmarkers = {bed_files[i]: b.shape[0] for i, b in enumerate(bims)}
    bim = pd.concat(bims, axis=0, ignore_index=True)
    del bim["i"]
    fam = _read_file(fam_files, lambda f: _read_fam(f), pbar)[0]
    del fam["i"]

    nsamples = fam.shape[0]
    sample_ids = fam["iid"]
    variant_ids = bim["chrom"] + "_" + bim["snp"]

    if ref == "a1":
        ref = Allele.a1
    elif ref == "a0":
        ref = Allele.a0
    else:
        raise ValueError("Unknown reference allele.")

    G = _read_file(
        bed_files, lambda f: _read_bed(f, nsamples, nmarkers[f], ref, chunk).T, pbar
    )
    G = da.concatenate(G, axis=1)

    G = DataArray(G, dims=["sample", "variant"], coords=[sample_ids, variant_ids])
    sample = {c: ("sample", fam[c]) for c in fam.columns}
    variant = {c: ("variant", bim[c]) for c in bim.columns}
    G = G.assign_coords(**sample)
    G = G.assign_coords(**variant)
    G.name = "genotype"

    pbar.close()

    return G


def _read_file(fn, read_func, pbar):
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
        names=list(header.keys()),
        dtype=header,
        compression=None,
        engine="c",
    )


def _read_bim(fn):
    from numpy import float64, int32

    header = odict(
        [
            ("chrom", object),
            ("snp", object),
            ("cm", float64),
            ("pos", int32),
            ("a0", object),
            ("a1", object),
        ]
    )
    df = _read_csv(fn, header)

    df["i"] = range(df.shape[0])
    return df


def _read_fam(fn):
    header = odict(
        [
            ("fid", object),
            ("iid", object),
            ("father", object),
            ("mother", object),
            ("gender", object),
            ("trait", object),
        ]
    )

    df = _read_csv(fn, header)

    df["i"] = range(df.shape[0])
    return df


def _read_bed(fn, nsamples, nvariants, ref: Allele, chunk: Chunk):
    _check_bed_header(fn)
    major = _major_order(fn)

    ncols = nvariants
    nrows = nsamples
    row_chunk = nrows if chunk.nsamples is None else min(nrows, chunk.nsamples)
    col_chunk = ncols if chunk.nvariants is None else min(ncols, chunk.nvariants)

    if major == "variant":
        nrows, ncols = ncols, nrows
        row_chunk, col_chunk = col_chunk, row_chunk

    return read_bed(fn, nrows, ncols, row_chunk, col_chunk, ref)


def _check_bed_header(fn):
    with open(fn, "rb") as f:
        arr = f.read(2)
        if len(arr) < 2:
            raise ValueError("Couldn't read BED header: %s." % fn)
        ok = arr[0] == 108 and arr[1] == 27
        if not ok:
            raise ValueError("Invalid BED file: %s." % fn)


def _major_order(fn):
    with open(fn, "rb") as f:
        f.seek(2)
        arr = f.read(1)
        if len(arr) < 1:
            raise ValueError("Couldn't read column order: %s." % fn)
        if arr[0] == 1:
            return "variant"
        elif arr[0] == 0:
            return "sample"
        msg = "Invalid matrix layout. Maybe it is a PLINK2 file?"
        msg += " PLINK2 is not supported yet."
        raise ValueError(msg)


def _clean_prefixes(prefixes):
    paths = []
    for p in prefixes:
        dirn = dirname(p)
        basen = basename(p)
        base = ".".join(basen.split(".")[:-1])
        if len(base) == 0:
            path = p
        else:
            ext = basen.split(".")[-1]
            if ext not in ["bed", "fam", "bim", "nosex", "log"]:
                base += "." + ext
            path = join(dirn, base)
        paths.append(path)
    return list(set(paths))
