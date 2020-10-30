from hashlib import md5
from os.path import dirname, join, realpath
from pathlib import Path

from numpy import dtype, nan
from numpy.testing import assert_array_equal, assert_equal

from pandas_plink import read_plink1_bin, write_plink1_bin


def test_write_plink1_bin(tmp_path: Path):

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = read_plink1_bin(bed, bim, fam, verbose=False)
    assert_equal(G.data.dtype, dtype("float32"))

    snp = G.where((G.chrom == "1") & (G.pos == 72515), drop=True)["snp"].values
    assert_array_equal(snp, ["rs4030300"])

    shape = G.where(G.chrom == "1", drop=True).shape
    assert_array_equal(shape, [3, 10])

    shape = G.where(G.chrom == "2", drop=True).shape
    assert_array_equal(shape, [3, 0])

    g = G.where((G.fid == "Sample_2") & (G.iid == "Sample_2"), drop=True)
    assert_array_equal(g["trait"].values, ["-9"])

    arr = [
        [2.0, 2.0, nan, nan, 2.0, 2.0, 2.0, 2.0, 1.0, 2.0],
        [2.0, 1.0, nan, nan, 2.0, 2.0, 1.0, 2.0, 2.0, 1.0],
        [1.0, 2.0, nan, 1.0, 2.0, 2.0, 0.0, 2.0, 2.0, 2.0],
    ]
    assert_array_equal(G, arr)

    write_plink1_bin(G, tmp_path / "out.bed")

    with open(bed, "rb") as f:
        bed_desired = md5(f.read()).hexdigest()

    with open(tmp_path / "out.bed", "rb") as f:
        bed_content = md5(f.read()).hexdigest()

    assert bed_content == bed_desired

    bim_desired = "88475a9ea7a52e056716e612f44ccb62"
    with open(tmp_path / "out.bim", "rb") as f:
        bim_content = md5(f.read()).hexdigest()
    assert bim_content == bim_desired

    fam_desired = "2df7b9a70ab70e95f8b1c774b9022404"
    with open(tmp_path / "out.fam", "rb") as f:
        fam_content = md5(f.read()).hexdigest()
    assert fam_content == fam_desired


def test_write_plink1_bin_filename(tmp_path: Path):

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = read_plink1_bin(bed, bim, fam, verbose=False)
    bedfp = tmp_path / "out.bed"
    bimfp = tmp_path / "out.bim"
    famfp = tmp_path / "out.fam"
    write_plink1_bin(G, bedfp, bimfp, famfp)

    with open(bed, "rb") as f:
        bed_desired = md5(f.read()).hexdigest()

    with open(tmp_path / "out.bed", "rb") as f:
        bed_content = md5(f.read()).hexdigest()

    assert bed_content == bed_desired

    bim_desired = "88475a9ea7a52e056716e612f44ccb62"
    with open(tmp_path / "out.bim", "rb") as f:
        bim_content = md5(f.read()).hexdigest()
    assert bim_content == bim_desired

    fam_desired = "2df7b9a70ab70e95f8b1c774b9022404"
    with open(tmp_path / "out.fam", "rb") as f:
        fam_content = md5(f.read()).hexdigest()
    assert fam_content == fam_desired


def test_write_plink1_bin_transpose(tmp_path: Path):

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = read_plink1_bin(bed, bim, fam, verbose=False)
    write_plink1_bin(G.T, tmp_path / "out.bed")

    with open(bed, "rb") as f:
        bed_desired = md5(f.read()).hexdigest()

    with open(tmp_path / "out.bed", "rb") as f:
        bed_content = md5(f.read()).hexdigest()

    assert bed_content == bed_desired

    bim_desired = "88475a9ea7a52e056716e612f44ccb62"
    with open(tmp_path / "out.bim", "rb") as f:
        bim_content = md5(f.read()).hexdigest()
    assert bim_content == bim_desired

    fam_desired = "2df7b9a70ab70e95f8b1c774b9022404"
    with open(tmp_path / "out.fam", "rb") as f:
        fam_content = md5(f.read()).hexdigest()
    assert fam_content == fam_desired


def test_write_plink1_bin_sample_major(tmp_path: Path):

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = read_plink1_bin(bed, bim, fam, verbose=False)
    write_plink1_bin(G, tmp_path / "tmp.bed", major="sample", verbose=False)

    G = read_plink1_bin(str(tmp_path / "tmp.bed"), verbose=False)
    write_plink1_bin(G, tmp_path / "out.bed", verbose=False)

    with open(bed, "rb") as f:
        bed_desired = md5(f.read()).hexdigest()

    with open(tmp_path / "out.bed", "rb") as f:
        bed_content = md5(f.read()).hexdigest()

    assert bed_content == bed_desired

    bim_desired = "88475a9ea7a52e056716e612f44ccb62"
    with open(tmp_path / "out.bim", "rb") as f:
        bim_content = md5(f.read()).hexdigest()
    assert bim_content == bim_desired

    fam_desired = "2df7b9a70ab70e95f8b1c774b9022404"
    with open(tmp_path / "out.fam", "rb") as f:
        fam_content = md5(f.read()).hexdigest()
    assert fam_content == fam_desired


def test_write_plink1_bin_empty_metadata(tmp_path: Path):

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = read_plink1_bin(bed, bim, fam, verbose=False)
    names = list(set(G.coords.keys()) - set(["sample", "variant"]))
    G = G.drop_vars(names)
    write_plink1_bin(G, tmp_path / "out.bed")

    with open(bed, "rb") as f:
        bed_desired = md5(f.read()).hexdigest()

    with open(tmp_path / "out.bed", "rb") as f:
        bed_content = md5(f.read()).hexdigest()

    assert bed_content == bed_desired

    bim_desired = "3dd5c109ba236d8b770d9c29dbc23c14"
    with open(tmp_path / "out.bim", "rb") as f:
        bim_content = md5(f.read()).hexdigest()
    assert bim_content == bim_desired

    fam_desired = "37dcb1a777a2a99ca3484b82cfb9c33b"
    with open(tmp_path / "out.fam", "rb") as f:
        fam_content = md5(f.read()).hexdigest()
    assert fam_content == fam_desired
