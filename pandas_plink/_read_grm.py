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
        array([[ 0.885782,  0.233846, -0.186339, -0.009789, -0.138897,  0.287779,
                 0.269977, -0.231279, -0.095472, -0.213979],
               [ 0.233846,  1.077490, -0.452858,  0.192877, -0.186027,  0.171027,
                 0.406056, -0.013149, -0.131477, -0.134314],
               [-0.186339, -0.452858,  1.183310, -0.040948, -0.146034, -0.204510,
                -0.314808, -0.042503,  0.296828, -0.011661],
               [-0.009789,  0.192877, -0.040948,  0.895360, -0.068605,  0.012023,
                 0.057827, -0.192152, -0.089094,  0.174269],
               [-0.138897, -0.186027, -0.146034, -0.068605,  1.183240,  0.085104,
                -0.032974,  0.103608,  0.215769,  0.166648],
               [ 0.287779,  0.171027, -0.204510,  0.012023,  0.085104,  0.956921,
                 0.065427, -0.043752, -0.091492, -0.227673],
               [ 0.269977,  0.406056, -0.314808,  0.057827, -0.032974,  0.065427,
                 0.714746, -0.101254, -0.088171, -0.063964],
               [-0.231279, -0.013149, -0.042503, -0.192152,  0.103608, -0.043752,
                -0.101254,  1.423030, -0.298255, -0.074333],
               [-0.095472, -0.131477,  0.296828, -0.089094,  0.215769, -0.091492,
                -0.088171, -0.298255,  0.910274, -0.024663],
               [-0.213979, -0.134314, -0.011661,  0.174269,  0.166648, -0.227673,
                -0.063964, -0.074333, -0.024663,  0.914586]])
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
        array([[ 0.789741,  0.101190, -0.194127, -0.068371, -0.265640,  0.151390,
                 0.196644, -0.270054, -0.181169, -0.259604],
               [ 0.101190,  1.072332, -0.447202,  0.041175, -0.339544, -0.013040,
                 0.233734, -0.149868, -0.251332, -0.247446],
               [-0.194127, -0.447202,  1.387866, -0.070182, -0.241946, -0.227255,
                -0.353192, -0.087077,  0.282681, -0.049566],
               [-0.068371,  0.041175, -0.070182,  0.819457, -0.161825, -0.131319,
                -0.051086, -0.295705, -0.166180,  0.084035],
               [-0.265640, -0.339544, -0.241946, -0.161825,  1.079747, -0.100829,
                -0.121493, -0.026588,  0.114705,  0.063413],
               [ 0.151390, -0.013040, -0.227255, -0.131319, -0.100829,  0.943739,
                -0.049455, -0.107822, -0.158418, -0.306991],
               [ 0.196644,  0.233734, -0.353192, -0.051086, -0.121493, -0.049455,
                 0.594578, -0.179436, -0.143500, -0.126795],
               [-0.270054, -0.149868, -0.087077, -0.295705, -0.026588, -0.107822,
                -0.179436,  1.491790, -0.324950, -0.050290],
               [-0.181169, -0.251332,  0.282681, -0.166180,  0.114705, -0.158418,
                -0.143500, -0.324950,  0.889190, -0.061028],
               [-0.259604, -0.247446, -0.049566,  0.084035,  0.063413, -0.306991,
                -0.126795, -0.050290, -0.061028,  0.954272]])
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
