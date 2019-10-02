from deprecated.sphinx import versionadded

from ._filetype import file_type
from ._util import last_replace


@versionadded(version="2.0.0")
def read_grm(filepath, id_filepath=None, n_snps_filepath=None):
    """
    Read GCTA realized relationship matrix files.

    A GRM file set consists of two or three files: (i) one containing the covariance
    matrix; (ii) one contaning sample IDs; and (iii) possibly another one containing
    the number of non-missing SNPs.

    It supports plain text, binary, and compressed files. The usual file extensions for
    those types are `.grm`, `grm.bin`, and `.grm.gz`, respectively.

    Example
    -------
    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_grm
        >>> from pandas_plink import get_data_folder
        >>> filepath = join(get_data_folder(), "grm-list", "plink2.grm")
        >>> id_filepath = join(get_data_folder(), "grm-list", "plink2.grm.id")
        >>> (K, n_snps) = read_grm(filepath, id_filepath)
        >>> print(K)
        <xarray.DataArray (sample_0: 10, sample_1: 10)>
        array([[ 0.89,  0.23, -0.19, -0.01, -0.14,  0.29,  0.27, -0.23, -0.10,
                -0.21],
               [ 0.23,  1.08, -0.45,  0.19, -0.19,  0.17,  0.41, -0.01, -0.13,
                -0.13],
               [-0.19, -0.45,  1.18, -0.04, -0.15, -0.20, -0.31, -0.04,  0.30,
                -0.01],
               [-0.01,  0.19, -0.04,  0.90, -0.07,  0.01,  0.06, -0.19, -0.09,
                 0.17],
               [-0.14, -0.19, -0.15, -0.07,  1.18,  0.09, -0.03,  0.10,  0.22,
                 0.17],
               [ 0.29,  0.17, -0.20,  0.01,  0.09,  0.96,  0.07, -0.04, -0.09,
                -0.23],
               [ 0.27,  0.41, -0.31,  0.06, -0.03,  0.07,  0.71, -0.10, -0.09,
                -0.06],
               [-0.23, -0.01, -0.04, -0.19,  0.10, -0.04, -0.10,  1.42, -0.30,
                -0.07],
               [-0.10, -0.13,  0.30, -0.09,  0.22, -0.09, -0.09, -0.30,  0.91,
                -0.02],
               [-0.21, -0.13, -0.01,  0.17,  0.17, -0.23, -0.06, -0.07, -0.02,
                 0.91]])
        Coordinates:
          * sample_0  (sample_0) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
          * sample_1  (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
            fid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
            iid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
        >>> print(n_snps)
        [50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50
         50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50
         50 50 50 50 50 50 50]
        >>> filepath = join(get_data_folder(), "grm-bin", "plink.grm.bin")
        >>> id_filepath = join(get_data_folder(), "grm-bin", "plink.grm.id")
        >>> n_snps_filepath = join(get_data_folder(), "grm-bin", "plink.grm.N.bin")
        >>> (K, n_snps) = read_grm(filepath, id_filepath, n_snps_filepath)
        >>> print(K)
        <xarray.DataArray (sample_0: 10, sample_1: 10)>
        array([[ 0.79,  0.10, -0.19, -0.07, -0.27,  0.15,  0.20, -0.27, -0.18,
                -0.26],
               [ 0.10,  1.07, -0.45,  0.04, -0.34, -0.01,  0.23, -0.15, -0.25,
                -0.25],
               [-0.19, -0.45,  1.39, -0.07, -0.24, -0.23, -0.35, -0.09,  0.28,
                -0.05],
               [-0.07,  0.04, -0.07,  0.82, -0.16, -0.13, -0.05, -0.30, -0.17,
                 0.08],
               [-0.27, -0.34, -0.24, -0.16,  1.08, -0.10, -0.12, -0.03,  0.11,
                 0.06],
               [ 0.15, -0.01, -0.23, -0.13, -0.10,  0.94, -0.05, -0.11, -0.16,
                -0.31],
               [ 0.20,  0.23, -0.35, -0.05, -0.12, -0.05,  0.59, -0.18, -0.14,
                -0.13],
               [-0.27, -0.15, -0.09, -0.30, -0.03, -0.11, -0.18,  1.49, -0.32,
                -0.05],
               [-0.18, -0.25,  0.28, -0.17,  0.11, -0.16, -0.14, -0.32,  0.89,
                -0.06],
               [-0.26, -0.25, -0.05,  0.08,  0.06, -0.31, -0.13, -0.05, -0.06,
                 0.95]])
        Coordinates:
          * sample_0  (sample_0) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
          * sample_1  (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
            fid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
            iid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
        >>> print(n_snps)
        [50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50
         50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50
         50 50 50 50 50 50 50]

    Parameters
    ----------
    filepath : str
        Path to the matrix file.
    id_filepath : str, optional
        Path to the file containing family and individual IDs. It defaults to ``None``,
        in which case it will try to be inferred.
    n_snps_filepath : str, optional
        Path to the file containing the number of non-missing SNPs. It defaults to
        ``None``, in which case it will try to be inferred.

    Returns
    -------
    grm : :class:`xarray.DataArray`
        Realized relationship matrix.
    n_snps : :class:`numpy.ndarray`
        Number of non-missing SNPs.
    """
    if file_type(filepath) == "bin":
        return _read_gcta_grm_bin(filepath, id_filepath, n_snps_filepath)
    return _read_gcta_grm(filepath, id_filepath)


def _read_gcta_grm(filepath, id_filepath):
    from pandas import read_csv
    from numpy import asarray, tril, zeros, int64
    from xarray import DataArray

    if filepath.endswith(".gz"):
        basename = filepath[:-3]
    else:
        basename = filepath

    if id_filepath is None:
        id_filepath = basename + ".id"

    df = read_csv(filepath, sep="\t", header=None)
    df_id = read_csv(id_filepath, sep="\t", header=None)
    n = int64(df.iloc[-1, 0])
    x = asarray(df.iloc[:, 0] - 1, int64)
    y = asarray(df.iloc[:, 1] - 1, int64)

    K = zeros((n, n))
    K[x, y] = df.iloc[:, 3]
    K = K + tril(K, -1).T
    coords = (df_id.iloc[:, 1], df_id.iloc[:, 1])
    K = DataArray(K, dims=["sample_0", "sample_1"], coords=coords)
    K = K.assign_coords(**{"fid": ("sample_0", df_id.iloc[:, 0])})
    K = K.assign_coords(**{"fid": ("sample_1", df_id.iloc[:, 0])})

    K = K.assign_coords(**{"iid": ("sample_0", df_id.iloc[:, 1])})
    K = K.assign_coords(**{"iid": ("sample_1", df_id.iloc[:, 1])})

    n_snps = asarray(df.iloc[:, 2], int64)

    return (K, n_snps)


def _read_gcta_grm_bin(filepath, id_filepath, n_snps_filepath):
    from pandas import read_csv
    from numpy import (
        asarray,
        tril,
        zeros,
        float32,
        fromfile,
        tril_indices_from,
        int64,
        float64,
    )
    from xarray import DataArray

    if id_filepath is None:
        id_filepath = last_replace(filepath, ".bin", ".id")

    if n_snps_filepath is None:
        n_snps_filepath = last_replace(filepath, ".bin", ".N.bin")

    df_id = read_csv(id_filepath, sep="\t", header=None)
    n = df_id.shape[0]
    k = asarray(fromfile(filepath, dtype=float32), float64)
    n_snps = asarray(fromfile(n_snps_filepath, dtype=float32), int64)

    K = zeros((n, n))
    K[tril_indices_from(K)] = k
    K = K + tril(K, -1).T
    coords = (df_id.iloc[:, 1], df_id.iloc[:, 1])
    K = DataArray(K, dims=["sample_0", "sample_1"], coords=coords)

    K = K.assign_coords(**{"fid": ("sample_0", df_id.iloc[:, 0])})
    K = K.assign_coords(**{"fid": ("sample_1", df_id.iloc[:, 0])})

    K = K.assign_coords(**{"iid": ("sample_0", df_id.iloc[:, 1])})
    K = K.assign_coords(**{"iid": ("sample_1", df_id.iloc[:, 1])})

    return (K, n_snps)
