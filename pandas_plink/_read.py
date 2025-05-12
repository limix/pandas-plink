import warnings
from collections import OrderedDict as odict
from glob import glob
from os.path import basename, dirname, join
from pathlib import Path
from typing import Callable, Optional, TypeVar, Union

from pandas import DataFrame, read_csv
from xarray import DataArray

from ._allele import Allele
from ._bed_read import read_bed
from ._chunk import Chunk
from ._util import last_replace

__all__ = ["read_plink", "read_plink1_bin"]


def read_plink(file_prefix: Union[str, Path], verbose=True):
    """
    Read PLINK files into data frames.

    .. note::

        The function :func:`pandas_plink.read_plink1_bin` provides an alternative
        interface to read the same files.

    The genotype values can be either :const:`0`, :const:`1`, :const:`2`, or
    :data:`math.nan`:

    - :const:`0` Homozygous having the first allele (given by coordinate **a0**)
    - :const:`1` Heterozygous
    - :const:`2` Homozygous having the second allele (given by coordinate **a1**)
    - :data:`math.nan` Missing genotype

    Examples
    --------
    The following example reads two BED files and two BIM files correspondig to
    chromosomes 11 and 12, and read a single FAM file whose filename is inferred from
    the BED filenames.

    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_plink
        >>> from pandas_plink import get_data_folder
        >>> (bim, fam, bed) = read_plink(join(get_data_folder(), "chr*.bed"),
        ...                              verbose=False)
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
    file_prefix : str | :class:`pathlib.Path`
        Path prefix to the set of PLINK files. It supports loading many BED files at
        once using globstrings wildcard.
    verbose : bool
        :const:`True` for progress information; :const:`False` otherwise.

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
    import pandera as pa
    from dask.array.core import Array, concatenate
    from tqdm import tqdm

    if isinstance(file_prefix, Path):
        root_dir = file_prefix.parent
        pathname = file_prefix.name
    else:
        root_dir = "."
        pathname = file_prefix

    prefixes = sorted(glob(pathname, root_dir=root_dir))
    if len(prefixes) == 0:
        prefixes = [pathname.replace("*", "")]

    prefixes = sorted(_clean_prefixes(prefixes))

    fn = [{s: "%s.%s" % (fp, s) for s in ["bed", "bim", "fam"]} for fp in prefixes]

    pbar = tqdm(desc="Mapping files", total=3 * len(fn), disable=not verbose)

    bim = _read_file([f["bim"] for f in fn], lambda fn: _read_bim(fn), pbar)
    if len(prefixes) > 1:
        if verbose:
            msg = "Multiple files read in this order: {}"
            print(msg.format([basename(f) for f in prefixes]))

    nmarkers = dict()
    index_offset = 0
    for i, bi in enumerate(bim):
        nmarkers[fn[i]["bed"]] = bi.shape[0]
        bi["i"] += index_offset
        index_offset += bi.shape[0]
    bim = pd.concat(bim, axis=0, ignore_index=True)

    fam = _read_file([fn[0]["fam"]], lambda fn: _read_fam(fn), pbar)[0]
    nsamples = fam.shape[0]

    ref = Allele.a1
    bed = _read_file(
        [f["bed"] for f in fn],
        lambda f: _read_bed(f, nsamples, nmarkers[f], ref, Chunk()).T,
        pbar,
    )

    bed = concatenate(bed, axis=0)
    assert isinstance(bed, Array)

    pbar.close()

    bim_schema = pa.DataFrameSchema(
        {
            "chrom": pa.Column(str),
            "snp": pa.Column(str),
            "cm": pa.Column("float64"),
            "pos": pa.Column("int32"),
            "a0": pa.Column(str),
            "a1": pa.Column(str),
            "i": pa.Column("int64"),
        }
    )
    fam_schema = pa.DataFrameSchema(
        {
            "fid": pa.Column(str),
            "iid": pa.Column(str),
            "father": pa.Column(str),
            "mother": pa.Column(str),
            "gender": pa.Column(str),
            "trait": pa.Column(str),
            "i": pa.Column("int64"),
        }
    )
    bim = bim_schema(bim)
    fam = fam_schema(fam)
    return (bim, fam, bed)


def read_plink1_bin(
    bed: Union[str, Path],
    bim: Optional[Union[str, Path]] = None,
    fam: Optional[Union[str, Path]] = None,
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
        Coordinates: (12/14)
          * sample   (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
          * variant  (variant) <U11 'variant0' 'variant1' ... 'variant1251'
            fid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            iid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            father   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            mother   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            ...       ...
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
        Coordinates: (12/14)
          * sample   (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
          * variant  (variant) <U11 'variant0' 'variant1' ... 'variant777' 'variant778'
            fid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            iid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
            father   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            mother   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
            ...       ...
            chrom    (variant) object '11' '11' '11' '11' '11' ... '11' '11' '11' '11'
            snp      (variant) object '316849996' '316874359' ... '345698259'
            cm       (variant) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0
            pos      (variant) int32 157439 181802 248969 ... 28937375 28961091 29005702
            a0       (variant) object 'C' 'G' 'G' 'C' 'C' 'T' ... 'A' 'C' 'A' 'A' 'T'
            a1       (variant) object 'T' 'C' 'C' 'T' 'T' 'A' ... 'G' 'T' 'G' 'C' 'C'
        >>> print(G.shape)
        (14, 779)

    Lets now print the genotype value of the sample `B003` for variant `variant5`:

    .. doctest::

        >>> print(G.sel(sample="B003", variant="variant5").values)
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
        BIM files. It defaults to :const:`None`, in which case it will try to be inferred.
    fam
        Path to a FAM file. It defaults to :const:`None`, in which case it will try to be
        inferred.
    verbose
        :const:`True` for progress information; :const:`False` otherwise.
    ref
        Reference allele. Specify which allele the dosage matrix will count. It can
        be either :const:`"a1"` (default) or :const:`"a0"`.
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
    import pandas as pd
    from dask.array.core import Array, concatenate
    from tqdm import tqdm

    if isinstance(bed, Path):
        bed_files = [str(bed.resolve())]
    else:
        bed_files = sorted(glob(bed))
    if len(bed_files) == 0:
        raise ValueError("No BED file has been found.")

    if bim is None:
        bim_files = [last_replace(f, ".bed", ".bim") for f in bed_files]
    elif isinstance(bim, Path):
        bim_files = [str(bim.resolve())]
    else:
        bim_files = sorted(glob(bim))
    if len(bim_files) == 0:
        raise ValueError("No BIM file has been found.")

    if fam is None:
        fam_files = [last_replace(f, ".bed", ".fam") for f in bed_files]
    elif isinstance(fam, Path):
        fam_files = [str(fam.resolve())]
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

    bims = _read_file(bim_files, lambda f: _read_bim_noi(f), pbar)
    nmarkers = {bed_files[i]: b.shape[0] for i, b in enumerate(bims)}
    bim_df = pd.concat(bims, axis=0, ignore_index=True)
    fam_df = _read_file(fam_files, lambda f: _read_fam_noi(f), pbar)[0]

    nsamples = fam_df.shape[0]
    sample_ids = [x for x in fam_df["iid"]]
    nvariants = bim_df.shape[0]
    variant_ids = [f"variant{i}" for i in range(nvariants)]

    if ref == "a1":
        ref_al = Allele.a1
    elif ref == "a0":
        ref_al = Allele.a0
    else:
        raise ValueError("Unknown reference allele.")

    G = _read_file(
        bed_files, lambda f: _read_bed(f, nsamples, nmarkers[f], ref_al, chunk), pbar
    )
    G = concatenate(G, axis=1)
    assert isinstance(G, Array)

    G = DataArray(G, dims=["sample", "variant"], coords=[sample_ids, variant_ids])
    sample = {c: ("sample", fam_df[c].to_list()) for c in fam_df.columns}
    variant = {c: ("variant", bim_df[c].to_list()) for c in iter(bim_df.columns)}
    G = G.assign_coords(sample)
    G = G.assign_coords(variant)
    G.name = "genotype"

    pbar.close()

    return G


T = TypeVar("T")


def _read_file(files: list[str], read_func: Callable[[str], T], pbar):
    data: list[T] = []
    for f in files:
        data.append(read_func(f))
        pbar.update(1)
    return data


def _read_csv(filename: str, header) -> DataFrame:
    df = read_csv(
        filename,
        sep=r"\s+",
        header=None,
        names=list(header.keys()),
        dtype=header,
        compression=None,
        engine="c",
        iterator=False,
    )
    assert isinstance(df, DataFrame)
    return df


def _read_bim(fn: str):
    df = _read_bim_noi(fn)
    df["i"] = range(df.shape[0])
    return df


def _read_bim_noi(fn: str):
    from ._type import bim

    header = odict(
        [
            ("chrom", bim["chrom"]),
            ("snp", bim["snp"]),
            ("cm", bim["cm"]),
            ("pos", bim["pos"]),
            ("a0", bim["a0"]),
            ("a1", bim["a1"]),
        ]
    )
    return _read_csv(fn, header)


def _read_fam(fn: str):
    df = _read_fam_noi(fn)
    df["i"] = range(df.shape[0])
    return df


def _read_fam_noi(fn: str):
    from ._type import fam

    header = odict(
        [
            ("fid", fam["fid"]),
            ("iid", fam["iid"]),
            ("father", fam["father"]),
            ("mother", fam["mother"]),
            ("gender", fam["gender"]),
            ("trait", fam["trait"]),
        ]
    )

    return _read_csv(fn, header)


def _read_bed(fn: str, nsamples: int, nvariants: int, ref: Allele, chunk: Chunk):
    from dask.array.core import Array

    _check_bed_header(fn)
    major = _major_order(fn)

    # Assume major == "variant".
    nrows = nvariants
    ncols = nsamples
    row_chunk = nrows if chunk.nvariants is None else min(nrows, chunk.nvariants)
    col_chunk = ncols if chunk.nsamples is None else min(ncols, chunk.nsamples)

    if major == "sample":
        nrows, ncols = ncols, nrows
        row_chunk, col_chunk = col_chunk, row_chunk

    max_npartitions = 16_384
    row_chunk = max(nrows // max_npartitions, row_chunk)
    col_chunk = max(ncols // max_npartitions, col_chunk)

    G = read_bed(fn, nrows, ncols, row_chunk, col_chunk, ref)
    if major == "variant":
        G = G.T

    assert isinstance(G, Array)
    return G


def _check_bed_header(fn: str):
    with open(fn, "rb") as f:
        arr = f.read(2)
        if len(arr) < 2:
            raise ValueError("Couldn't read BED header: %s." % fn)
        ok = arr[0] == 108 and arr[1] == 27
        if not ok:
            raise ValueError("Invalid BED file: %s." % fn)


def _major_order(fn: str):
    """
    Major order.

    Variant-major lists all samples for first variant, all samples for second
    variant, and so on. Sample-major lists all variants for first sample, all
    variants for second sample, and so on.
    """
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
