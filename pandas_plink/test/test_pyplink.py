from __future__ import unicode_literals

from os.path import dirname, realpath, join
import pytest

from numpy.testing import assert_array_equal
from numpy import array, nan
from pandas_plink import read_plink

@pytest.mark.datafiles(join(dirname(realpath(__file__)), 'data_files'))
def test_bla(datafiles):
    file_prefix = join(str(datafiles), 'data')

    (bim, fam, bed) = read_plink(file_prefix)

    assert_array_equal(bim.loc[('1', 72515), 'snp'], ['rs4030300'])
    assert_array_equal(bim.loc[('1', ), :].shape, [10, 4])
    assert_array_equal(fam.loc[('Sample_2', 'Sample_2'), 'trait'],
                       ['-9'])

    assert_array_equal(bed, array([[ nan,  nan,   2.],
        [ nan,   2.,  nan],
        [  1.,   1.,   1.],
        [  1.,   1.,   2.],
        [ nan,  nan,  nan],
        [ nan,  nan,  nan],
        [ nan,   2.,   0.],
        [ nan,  nan,  nan],
        [  2.,  nan,  nan],
        [ nan,   2.,  nan]]))
