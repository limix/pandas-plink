import warnings
from collections import OrderedDict as odict
from glob import glob
from os.path import basename, dirname, join
from typing import Optional

from pandas import StringDtype
from xarray import DataArray

from ._allele import Allele
from ._bed_read import read_bed
from ._chunk import Chunk
from ._util import last_replace

__all__ = ["read_plink", "read_plink1_bin"]


def read_plink(file_prefix, verbose=True):
    """
    Read PLINK files into data frames.

    .. note::

        The function :func:`pandas_plink.read_plink1_bin` provides an alternative
        interface to read the same files.

    The genotype values can be either ``0``, ``1``, ``2``, or ``NaN``:

    - ``0`` Homozygous having the first allele (given by coordinate ``a0``)
    - ``1`` Heterozygous
    - ``2`` Homozygous having the second allele (given by coordinate ``a1``)
    - ``NaN`` Missing genotype

    Examples
    --------
    The following example reads two BED files and two BIM files correspondig to
    chromosomes 11 and 12, and read a single FAM file whose filename is inferred from
    the BED filenames.

    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_plink
        >>> from pandas_plink import get_data_folder
        >>> (bim, fam, bed) = read_plink(join(get_data_folder(), "chr*.bed"), verbose=False)
        >>> print(bim.head())
          chrom        snp       cm     pos a0 a1  i
        0    11  316849996     0.00  157439  C  T  0
        1    11  316874359     0.00  181802  G  C  1
        2    11  316941526     0.00  248969  G  C  2
        3    11  317137620     0.00  445063  C  T  3
        4    11  317534352     0.00  841795  C  T  4
        >>> print(fam.head())
            fid   iid father mother gender trait  i
        0  B001  B001      0      0      0    -9  0
        1  B002  B002      0      0      0    -9  1
        2  B003  B003      0      0      0    -9  2
        3  B004  B004      0      0      0    -9  3
        4  B005  B005      0      0      0    -9  4
        >>> print(bed.compute())
        [[0.00 0.00 0.00 ... 2.00 2.00 0.00]
         [0.00 1.00 0.00 ... 2.00 1.00 0.00]
         [2.00 2.00 2.00 ... 0.00 0.00 2.00]
         ...
         [2.00 0.00 0.00 ... 2.00 2.00 1.00]
         [2.00 0.00 0.00 ... 2.00 2.00 0.00]
         [0.00  nan 0.00 ... 1.00 2.00 0.00]]

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
    genotypes : :class:`dask.array.Array`
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
    bed: str,
    bim: Optional[str] = None,
    fam: Optional[str] = None,
    verbose: bool = True,
    ref: str = "a1",
    chunk: Chunk = Chunk(),
) -> DataArray:
    """
    Read PLINK 1 binary files [a]_ into a data array.

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
    bed
        Path to a BED file. It can contain shell-style wildcards to indicate multiple
        BED files.
    bim
        Path to a BIM file. It can contain shell-style wildcards to indicate multiple
        BIM files. It defaults to ``None``, in which case it will try to be inferred.
    fam
        Path to a FAM file. It defaults to ``None``, in which case it will try to be
        inferred.
    verbose
        ``True`` for progress information; ``False`` otherwise.
    ref
        Reference allele. Specify which allele the dosage matrix will count. It can
        be either ``"a1"`` (default) or ``"a0"``.
    chunk
        Data chunk specification. Useful to adjust the trade-off between computational
        overhead and IO usage. See :class:`pandas_plink.Chunk`.

    Returns
    -------
    :class:`xarray.DataArray`
        Genotype with metadata.

    References
    ----------
    .. [a] PLINK 1 binary. https://www.cog-genomics.org/plink/2.0/input#bed
    """
    import dask.array as da
    import pandas as pd
    from tqdm import tqdm

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
    bim_df = pd.concat(bims, axis=0, ignore_index=True)
    del bim_df["i"]
    fam_df = _read_file(fam_files, lambda f: _read_fam(f), pbar)[0]
    del fam_df["i"]

    nsamples = fam_df.shape[0]
    sample_ids = fam_df["iid"]
    variant_ids = bim_df[["chrom", "snp"]].agg("_".join, axis=1)

    if ref == "a1":
        ref_al = Allele.a1
    elif ref == "a0":
        ref_al = Allele.a0
    else:
        raise ValueError("Unknown reference allele.")

    G = _read_file(
        bed_files, lambda f: _read_bed(f, nsamples, nmarkers[f], ref_al, chunk).T, pbar
    )
    G = da.concatenate(G, axis=1)

    G = DataArray(G, dims=["sample", "variant"], coords=[sample_ids, variant_ids])
    sample = {c: ("sample", fam_df[c]) for c in fam_df.columns}
    variant = {c: ("variant", bim_df[c]) for c in bim_df.columns}
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
            ("chrom", StringDtype()),
            ("snp", StringDtype()),
            ("cm", float64),
            ("pos", int32),
            ("a0", StringDtype()),
            ("a1", StringDtype()),
        ]
    )
    df = _read_csv(fn, header)

    df["i"] = range(df.shape[0])
    return df


def _read_fam(fn):
    header = odict(
        [
            ("fid", StringDtype()),
            ("iid", StringDtype()),
            ("father", StringDtype()),
            ("mother", StringDtype()),
            ("gender", StringDtype()),
            ("trait", StringDtype()),
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

    G = read_bed(fn, nrows, ncols, row_chunk, col_chunk, ref)
    if major == "sample":
        G = G.T

    return G


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
