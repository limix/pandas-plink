from pathlib import Path
from typing import Optional, Union

from numpy import arange, full
from pandas import DataFrame, array
from xarray import DataArray

from ._bed_write import write_bed

__all__ = ["write_plink1_bin"]


def write_plink1_bin(
    G: DataArray,
    bed: Union[str, Path],
    bim: Optional[Union[str, Path]] = None,
    fam: Optional[Union[str, Path]] = None,
    major: str = "variant",
    verbose: bool = True,
):
    """
    Write PLINK 1 binary files into a data array.

    A PLINK 1 binary file set consists of three files:

    - BED: containing the genotype.
    - BIM: containing variant information.
    - FAM: containing sample information.

    The user must provide the genotype (dosage) via a :class:`xarray.DataArray` matrix
    with data type :const:`numpy.float32` or :const:`numpy.float64`. That matrix must
    have two named dimensions: **sample** and **variant**. The only allowed values for
    the genotype are: :const:`0`, :const:`1`, :const:`2`, and :data:`math.nan`.

    Examples
    --------
    .. testsetup:

        >>> import os
        >>> import shutil
        >>> import tempfile
        >>>
        >>> old_path = os.getcwd()
        >>> tmp_path = tempfile.mkdtemp()
        >>> os.chdir(tmp_path)

    The following example produces a BED file with data.

    .. doctest::

        >>> from xarray import DataArray
        >>> from pandas_plink import read_plink1_bin, write_plink1_bin
        >>>
        >>> G = DataArray(
        ...     [[3.0, 2.0, 2.0], [0.0, 0.0, 1.0]],
        ...     dims=["sample", "variant"],
        ...     coords = dict(
        ...         sample  = ["boffy", "jolly"],
        ...         fid     = ("sample", ["humin"] * 2 ),
        ...
        ...         variant = ["not", "sure", "what"],
        ...         snp     = ("variant", ["rs1", "rs2", "rs3"]),
        ...         chrom   = ("variant", ["1", "1", "2"]),
        ...         a0      = ("variant", ['A', 'T', 'G']),
        ...         a1      = ("variant", ['C', 'A', 'T']),
        ...     )
        ... )
        >>>
        >>> print(G)
        <xarray.DataArray (sample: 2, variant: 3)>
        array([[3.00, 2.00, 2.00],
               [0.00, 0.00, 1.00]])
        Coordinates:
          * sample   (sample) <U5 'boffy' 'jolly'
            fid      (sample) <U5 'humin' 'humin'
          * variant  (variant) <U4 'not' 'sure' 'what'
            snp      (variant) <U3 'rs1' 'rs2' 'rs3'
            chrom    (variant) <U1 '1' '1' '2'
            a0       (variant) <U1 'A' 'T' 'G'
            a1       (variant) <U1 'C' 'A' 'T'
        >>> write_plink1_bin(G, "sample.bed", verbose=False)
        >>>
        >>> G = read_plink1_bin("sample.bed", verbose=False)
        >>> print(G)
        <xarray.DataArray 'genotype' (sample: 2, variant: 3)>
        dask.array<transpose, shape=(2, 3), dtype=float32, chunksize=(2, 3), chunktype=numpy.ndarray>
        Coordinates: (12/14)
          * sample   (sample) object 'boffy' 'jolly'
          * variant  (variant) <U8 'variant0' 'variant1' 'variant2'
            fid      (sample) object 'humin' 'humin'
            iid      (sample) object 'boffy' 'jolly'
            father   (sample) object '?' '?'
            mother   (sample) object '?' '?'
            ...       ...
            chrom    (variant) object '1' '1' '2'
            snp      (variant) object 'rs1' 'rs2' 'rs3'
            cm       (variant) float64 0.0 0.0 0.0
            pos      (variant) int32 0 0 0
            a0       (variant) object 'A' 'T' 'G'
            a1       (variant) object 'C' 'A' 'T'

    The following example reads two BED files and two BIM files correspondig to
    chromosomes 11 and 12, and read a single FAM file whose filename is inferred from
    the BED filenames. It then saves the resulting matrix to disk.

    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_plink1_bin, write_plink1_bin
        >>> from pandas_plink import get_data_folder
        >>>
        >>> G = read_plink1_bin(join(get_data_folder(), "chr*.bed"), verbose=False)
        >>> write_plink1_bin(G, "all.bed", verbose=False)
        >>> G = read_plink1_bin("all.bed", verbose=False)
        >>> print(G)
        <xarray.DataArray 'genotype' (sample: 14, variant: 1252)>
        dask.array<transpose, shape=(14, 1252), dtype=float32, chunksize=(14, 1024), chunktype=numpy.ndarray>
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

    .. testcleanup::

        >>> os.chdir(old_path)
        >>> shutil.rmtree(tmp_path, ignore_errors=True)

    Parameters
    ----------
    G
        Genotype matrix with metainformation about samples and variants.
    bed
        Path to a BED file.
    bim
        Path to a BIM file.It defaults to :const:`None`, in which case it will try to be
        inferred.
    fam
        Path to a FAM file. It defaults to :const:`None`, in which case it will try to
        be inferred.
    major
        It can be either :const:`"sample"` or :const:`"variant"` (recommended and
        default). Specify the matrix layout on the BED file.
    verbose
        :const:`True` for progress information; :const:`False` otherwise.
    """
    if G.ndim != 2:
        raise ValueError("G has to be bidimensional")

    if set(list(G.dims)) != set(["sample", "variant"]):
        raise ValueError("G has to have both `sample` and `variant` dimensions.")

    if major not in ["sample", "variant"]:
        raise ValueError("Major can be either `sample` or `variant`.")

    G = G.transpose("sample", "variant")

    bed = Path(bed)

    if bim is None:
        bim = bed.with_suffix(".bim")

    if fam is None:
        fam = bed.with_suffix(".fam")

    bim = Path(bim)
    fam = Path(fam)

    G = _fill_sample(G)
    G = _fill_variant(G)
    write_bed(bed, G, major, verbose)

    _echo("Writing FAM... ", end="", disable=not verbose)
    _write_fam(fam, G)
    _echo("done.", disable=not verbose)

    _echo("Writing BIM... ", end="", disable=not verbose)
    _write_bim(bim, G)
    _echo("done.", disable=not verbose)


def _echo(msg: str, end: str = "\n", disable: bool = False):
    if not disable:
        print(msg, end=end, flush=True)


def _fill_sample(G: DataArray) -> DataArray:
    from ._type import fam

    nsamples = G.sample.shape[0]
    if "fid" not in G.sample.coords:
        G = G.assign_coords(fid=("sample", G.sample.values))

    if "iid" not in G.sample.coords:
        G = G.assign_coords(iid=("sample", G.sample.values))

    if "father" not in G.sample.coords:
        G = G.assign_coords(father=("sample", array(["?"] * nsamples, fam["father"])))

    if "mother" not in G.sample.coords:
        G = G.assign_coords(mother=("sample", array(["?"] * nsamples, fam["mother"])))

    if "gender" not in G.sample.coords:
        G = G.assign_coords(gender=("sample", array(["0"] * nsamples, fam["gender"])))

    if "trait" not in G.sample.coords:
        G = G.assign_coords(trait=("sample", array(["-0"] * nsamples, fam["trait"])))
    return G


def _fill_variant(G: DataArray) -> DataArray:
    from ._type import bim

    nvariants = G.variant.shape[0]
    if "chrom" not in G.variant.coords:
        G = G.assign_coords(chrom=("variant", array(["?"] * nvariants, bim["chrom"])))

    if "snp" not in G.variant.coords:
        G = G.assign_coords(snp=("variant", array(arange(nvariants), bim["snp"])))

    if "cm" not in G.variant.coords:
        G = G.assign_coords(cm=("variant", full(nvariants, 0.0, bim["cm"])))

    if "pos" not in G.variant.coords:
        G = G.assign_coords(pos=("variant", full(nvariants, 0.0, bim["pos"])))

    if "a0" not in G.variant.coords:
        G = G.assign_coords(a0=("variant", array(["?"] * nvariants, bim["a0"])))

    if "a1" not in G.variant.coords:
        G = G.assign_coords(a1=("variant", array(["?"] * nvariants, bim["a1"])))
    return G


def _write_fam(filepath: Path, G: DataArray):
    from ._type import fam

    df = DataFrame()
    cols = [
        ("fid", fam["fid"]),
        ("iid", fam["iid"]),
        ("father", fam["father"]),
        ("mother", fam["mother"]),
        ("gender", fam["gender"]),
        ("trait", fam["trait"]),
    ]

    for col, col_type in cols:
        df[col] = G.sample[col].values
        df[col] = df[col].astype(col_type)

    df.to_csv(
        filepath,
        index=False,
        sep="\t",
        header=False,
        encoding="ascii",
        lineterminator="\n",
    )


def _write_bim(filepath: Path, G: DataArray):
    from ._type import bim

    df = DataFrame()
    cols = [
        ("chrom", bim["chrom"]),
        ("snp", bim["snp"]),
        ("cm", bim["cm"]),
        ("pos", bim["pos"]),
        ("a0", bim["a0"]),
        ("a1", bim["a1"]),
    ]

    for col, col_type in cols:
        df[col] = G.variant[col].values
        df[col] = df[col].astype(col_type)

    df.to_csv(
        filepath,
        index=False,
        sep="\t",
        header=False,
        encoding="ascii",
        lineterminator="\n",
    )
