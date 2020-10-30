from pathlib import Path
from typing import Optional, Union

from numpy import arange, float64, full, int32
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
    have two named dimensions: ``sample`` and ``variant``. The only allowed values for
    the genotype are: :data:`0`, :data:`1`, :data:`2`, and :data:`math.nan`.

    Examples
    --------
    .. doctest::

        >>> from xarray import DataArray
        >>> from pandas_plink import read_plink1_bin, write_plink1_bin
        >>>
        >>> G = DataArray([[0.0]], dims=["sample", "variant"])
        >>> write_plink1_bin(G, "sample.bed", verbose=False)
        >>> print(G)
        <xarray.DataArray (sample: 1, variant: 1)>
        array([[0.00]])
        Dimensions without coordinates: sample, variant
        >>> G = read_plink1_bin("sample.bed", verbose=False)
        >>> print(G)
        <xarray.DataArray 'genotype' (sample: 1, variant: 1)>
        dask.array<transpose, shape=(1, 1), dtype=float32, chunksize=(1, 1), chunktype=numpy.ndarray>
        Coordinates:
          * sample   (sample) object '0'
          * variant  (variant) object '?_0'
            fid      (sample) object '0'
            iid      (sample) object '0'
            father   (sample) object '?'
            mother   (sample) object '?'
            gender   (sample) object '0'
            trait    (sample) object '-9'
            chrom    (variant) object '?'
            snp      (variant) object '0'
            cm       (variant) float64 0.0
            pos      (variant) int32 0
            a0       (variant) object '?'
            a1       (variant) object '?'

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

    Parameters
    ----------
    G
        Genotype matrix with metainformation about samples and variants.
    bed
        Path to a BED file.
    bim
        Path to a BIM file.It defaults to ``None``, in which case it will try to be
        inferred.
    fam
        Path to a FAM file. It defaults to ``None``, in which case it will try to be
        inferred.
    major
        It can be either ``"sample"`` or ``"variant"`` (recommended and default).
        Specify the matrix layout on the BED file.
    verbose
        ``True`` for progress information; ``False`` otherwise.
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
    nsamples = G.sample.shape[0]
    if "fid" not in G.sample.coords:
        G = G.assign_coords(fid=("sample", G.sample.values))

    if "iid" not in G.sample.coords:
        G = G.assign_coords(iid=("sample", G.sample.values))

    if "father" not in G.sample.coords:
        G = G.assign_coords(father=("sample", full(nsamples, "?", object)))

    if "mother" not in G.sample.coords:
        G = G.assign_coords(mother=("sample", full(nsamples, "?", object)))

    if "gender" not in G.sample.coords:
        G = G.assign_coords(gender=("sample", full(nsamples, "0", object)))

    if "trait" not in G.sample.coords:
        G = G.assign_coords(trait=("sample", full(nsamples, "-9", object)))
    return G


def _fill_variant(G: DataArray) -> DataArray:
    nvariants = G.variant.shape[0]
    if "chrom" not in G.variant.coords:
        G = G.assign_coords(chrom=("variant", full(nvariants, "?", object)))

    if "snp" not in G.variant.coords:
        G = G.assign_coords(snp=("variant", arange(nvariants, dtype=object)))

    if "cm" not in G.variant.coords:
        G = G.assign_coords(cm=("variant", full(nvariants, 0.0, float64)))

    if "pos" not in G.variant.coords:
        G = G.assign_coords(pos=("variant", full(nvariants, 0.0, int32)))

    if "a0" not in G.variant.coords:
        G = G.assign_coords(a0=("variant", full(nvariants, "?", object)))

    if "a1" not in G.variant.coords:
        G = G.assign_coords(a1=("variant", full(nvariants, "?", object)))
    return G


def _write_fam(filepath: Path, G: DataArray):
    from pandas import DataFrame

    df = DataFrame()
    cols = [
        ("fid", object),
        ("iid", object),
        ("father", object),
        ("mother", object),
        ("gender", object),
        ("trait", object),
    ]

    for col, col_type in cols:
        df[col] = G.sample[col].values.astype(col_type)

    df.to_csv(
        filepath,
        index=False,
        sep="\t",
        header=None,
        encoding="ascii",
        line_terminator="\n",
    )


def _write_bim(filepath: Path, G: DataArray):
    from pandas import DataFrame

    df = DataFrame()
    cols = [
        ("chrom", object),
        ("snp", object),
        ("cm", float64),
        ("pos", int32),
        ("a0", object),
        ("a1", object),
    ]

    for col, col_type in cols:
        df[col] = G.variant[col].values.astype(col_type)

    df.to_csv(
        filepath,
        index=False,
        sep="\t",
        header=None,
        encoding="ascii",
        line_terminator="\n",
    )
