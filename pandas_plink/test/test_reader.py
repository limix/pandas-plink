from os.path import dirname, join, realpath

import pytest
from numpy import array, dtype, nan
from numpy.testing import assert_array_equal, assert_equal

from pandas_plink import example_file_prefix, read_plink, read_plink1_bin


def test_read_plink():

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")

    (bim, fam, bed) = read_plink(file_prefix, verbose=False)
    assert_equal(bed.dtype, dtype("float64"))

    assert_array_equal(bim.query("chrom=='1' and pos==72515")["snp"], ["rs4030300"])
    assert_array_equal(bim.query("chrom=='1'").shape, [10, 7])
    assert_array_equal(fam.query("fid=='Sample_2' and iid=='Sample_2'")["trait"], [-9])

    assert_array_equal(
        bed,
        array(
            [
                [2, 2, 1],
                [2, 1, 2],
                [nan, nan, nan],
                [nan, nan, 1],
                [2, 2, 2],
                [2, 2, 2],
                [2, 1, 0],
                [2, 2, 2],
                [1, 2, 2],
                [2, 1, 2],
            ]
        ),
    )


def test_read_plink_prefix_dot():

    with pytest.raises(IOError):
        read_plink("/home/joao/84757.genotypes.norm.renamed")


def test_read_plink_wildcard():
    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "chr*")

    (bim, fam, bed) = read_plink(file_prefix, verbose=False)
    assert_array_equal(bim[bim["chrom"] == "11"]["i"].values[:2], [0, 1])
    assert_array_equal(bim[bim["chrom"] == "12"]["i"].values[:2], [779, 780])


def test_read_plink1_bin():

    datafiles = join(dirname(realpath(__file__)), "data_files")
    file_prefix = join(datafiles, "data")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = read_plink1_bin(bed, bim, fam, verbose=False)
    assert_equal(G.data.dtype, dtype("float64"))

    snp = G.where((G.chrom == "1") & (G.pos == 72515), drop=True)["snp"].values
    assert_array_equal(snp, ["rs4030300"])

    shape = G.where(G.chrom == "1", drop=True).shape
    assert_array_equal(shape, [3, 10])

    shape = G.where(G.chrom == "2", drop=True).shape
    assert_array_equal(shape, [3, 0])

    g = G.where((G.fid == "Sample_2") & (G.iid == "Sample_2"), drop=True)
    assert_array_equal(g["trait"].values, -9)

    arr = [
        [2.0, 2.0, nan, nan, 2.0, 2.0, 2.0, 2.0, 1.0, 2.0],
        [2.0, 1.0, nan, nan, 2.0, 2.0, 1.0, 2.0, 2.0, 1.0],
        [1.0, 2.0, nan, 1.0, 2.0, 2.0, 0.0, 2.0, 2.0, 2.0],
    ]
    assert_array_equal(G, arr)


def test_read_plink1_bin_wildcard_not_found():
    datafiles = join(dirname(realpath(__file__)), "data_files")
    bed_files = join(datafiles, "chrr*.bed")

    with pytest.raises(ValueError):
        read_plink1_bin(bed_files, verbose=False)

    bed_files = join(datafiles, "chr*.bed")
    with pytest.raises(ValueError):
        read_plink1_bin(bed_files, "chr11.bim", verbose=False)

    bed_files = join(datafiles, "chr*.bed")
    bim_files = join(datafiles, "chrr*.bim")
    with pytest.raises(ValueError):
        read_plink1_bin(bed_files, bim_files, verbose=False)

    bed_files = join(datafiles, "chr*.bed")
    bim_files = join(datafiles, "chr*.bim")
    fam_files = join(datafiles, "chr*.fam")
    with pytest.warns(UserWarning):
        read_plink1_bin(bed_files, bim_files, fam_files, verbose=True)


def test_read_plink1_bin_wildcard():
    datafiles = join(dirname(realpath(__file__)), "data_files")
    bed_files = join(datafiles, "chr*.bed")

    G = read_plink1_bin(bed_files, verbose=False)
    G.where(G.chrom == "11", drop=True).values
    assert_equal(G.where(G.chrom == "11", drop=True).shape, (14, 779))
    assert_equal(G.where(G.chrom == "12", drop=True).shape, (14, 473))
    x = [[0.00, 0.00], [0.00, 1.00]]
    assert_equal(G.where(G.chrom == "11", drop=True).values[:2, :2], x)


def test_example_file_prefix():
    with pytest.warns(DeprecationWarning):
        example_file_prefix()
