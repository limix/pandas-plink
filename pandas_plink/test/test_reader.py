from __future__ import unicode_literals

from os.path import dirname, join, realpath

from numpy import array
from numpy.testing import assert_array_equal

from pandas_plink import read_plink

def _ascii_airlock(v):
    if not isinstance(v, bytes):
        v = v.encode()
    return v

def test_read_plink():

    datafiles = join(dirname(realpath(__file__)), 'data_files')
    file_prefix = join(datafiles, 'data')

    (bim, fam, bed) = read_plink(file_prefix)

    assert_array_equal(bim.query("chrom=='1' and pos==72515")['snp'], ['rs4030300'])
    assert_array_equal(bim.query("chrom=='1'").shape, [10, 7])
    assert_array_equal(fam.query("fid=='Sample_2' and iid=='Sample_2'")["trait"], ['-9'])

    assert_array_equal(bed,
                       array([[2, 2, 1], [2, 1, 2], [3, 3, 3], [3, 3, 1],
                              [2, 2, 2], [2, 2, 2], [2, 1, 0], [2, 2, 2],
                              [1, 2, 2], [2, 1, 2]]))

