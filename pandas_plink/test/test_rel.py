from pandas_plink import read_rel
from os.path import dirname, join, realpath
from numpy.testing import assert_almost_equal, assert_equal


def test_read_rel():
    datafiles = join(dirname(realpath(__file__)), "data_files")

    filepath = join(datafiles, "rel", "plink.rel")
    K = read_rel(filepath)
    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.789741, -0.158418])
    assert_equal(K.sample_0[4].data, "NA12489")

    filepath = join(datafiles, "rel", "plink.rel")
    filepath_id = join(datafiles, "rel", "plink.rel.id")
    K = read_rel(filepath, filepath_id)
    assert_almost_equal([K.data[0, 0], K.data[-2, 5]], [0.789741, -0.158418])
    assert_equal(K.sample_0[4].data, "NA12489")


def test_read_rel_bin():
    datafiles = join(dirname(realpath(__file__)), "data_files")

    filepath = join(datafiles, "rel-bin", "plink2.rel.bin")
    K = read_rel(filepath, binary=True)
    assert_almost_equal(
        [K.data[0, 0], K.data[-2, 5]], [0.8857815151328152, -0.09149171449203966]
    )
    assert_equal(K.sample_0[4].data, "NA12489")

    filepath = join(datafiles, "rel-bin", "plink2.rel.bin")
    filepath_id = join(datafiles, "rel-bin", "plink2.rel.id")
    K = read_rel(filepath, filepath_id, binary=True)
    assert_almost_equal(
        [K.data[0, 0], K.data[-2, 5]], [0.8857815151328152, -0.09149171449203966]
    )
    assert_equal(K.sample_0[4].data, "NA12489")
