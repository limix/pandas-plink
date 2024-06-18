from os.path import dirname, join, realpath

from numpy.testing import assert_almost_equal, assert_equal

from pandas_plink import read_grm


def test_read_grm():
    datafiles = join(dirname(realpath(__file__)), "data_files")
    filepath = join(datafiles, "grm-list", "plink2.grm")
    (K, n_snps) = read_grm(filepath)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.885782, -0.0914917])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)

    filepath = join(datafiles, "grm-list", "plink2.grm")
    filepath_id = join(datafiles, "grm-list", "plink2.grm.id")
    (K, n_snps) = read_grm(filepath, filepath_id)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.885782, -0.0914917])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)


def test_read_grm_gz():
    datafiles = join(dirname(realpath(__file__)), "data_files")

    filepath = join(datafiles, "grm-gz", "plink.grm.gz")
    (K, n_snps) = read_grm(filepath)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.78974109888, -0.15841817856])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)

    filepath = join(datafiles, "grm-gz", "plink.grm.gz")
    filepath_id = join(datafiles, "grm-gz", "plink.grm.id")
    (K, n_snps) = read_grm(filepath, filepath_id)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.78974109888, -0.15841817856])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)


def test_read_grm_bin():
    datafiles = join(dirname(realpath(__file__)), "data_files")

    filepath = join(datafiles, "grm-bin", "plink.grm.bin")
    (K, n_snps) = read_grm(filepath)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.78974109888, -0.15841817856])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)

    filepath = join(datafiles, "grm-bin", "plink.grm.bin")
    filepath_id = join(datafiles, "grm-bin", "plink.grm.id")
    (K, n_snps) = read_grm(filepath, filepath_id)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.78974109888, -0.15841817856])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)

    filepath = join(datafiles, "grm-bin", "plink.grm.bin")
    filepath_id = join(datafiles, "grm-bin", "plink.grm.id")
    filepath_n_snps = join(datafiles, "grm-bin", "plink.grm.N.bin")
    (K, n_snps) = read_grm(filepath, filepath_id, filepath_n_snps)

    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.78974109888, -0.15841817856])
    assert_equal(K.sample_0[4].data, "NA12489")
    assert_equal(n_snps[3], 50)
