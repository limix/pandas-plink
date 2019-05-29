from deprecated.sphinx import versionadded

from ._filetype import file_type


@versionadded(version="2.0.0")
def read_rel(filepath, id_filepath=None):
    """
    Read PLINK realized relationship matrix files [1]_.

    It supports plain text, binary, and compressed files.
    The usual file extensions for those types are `.rel`, `.rel.bin`, and `.rel.zst`,
    respectively.

    Example
    -------
    .. doctest::

        >>> from os.path import join
        >>> from pandas_plink import read_rel
        >>> from pandas_plink import get_data_folder
        >>> filepath = join(get_data_folder(), "rel-bin", "plink2.rel.bin")
        >>> id_filepath = join(get_data_folder(), "rel-bin", "plink2.rel.id")
        >>> K = read_rel(filepath, id_filepath)
        >>> print(K)
        <xarray.DataArray (sample_0: 10, sample_1: 10)>
        array([[ 0.885782,  0.233846, -0.186339, -0.009789, -0.138897,  0.287779,
                 0.269977, -0.231279, -0.095472, -0.213979],
               [ 0.233846,  1.077493, -0.452858,  0.192877, -0.186027,  0.171027,
                 0.406056, -0.013149, -0.131477, -0.134314],
               [-0.186339, -0.452858,  1.183312, -0.040948, -0.146034, -0.204510,
                -0.314808, -0.042503,  0.296828, -0.011661],
               [-0.009789,  0.192877, -0.040948,  0.895360, -0.068605,  0.012023,
                 0.057827, -0.192152, -0.089094,  0.174269],
               [-0.138897, -0.186027, -0.146034, -0.068605,  1.183237,  0.085104,
                -0.032974,  0.103608,  0.215769,  0.166648],
               [ 0.287779,  0.171027, -0.204510,  0.012023,  0.085104,  0.956921,
                 0.065427, -0.043752, -0.091492, -0.227673],
               [ 0.269977,  0.406056, -0.314808,  0.057827, -0.032974,  0.065427,
                 0.714746, -0.101254, -0.088171, -0.063964],
               [-0.231279, -0.013149, -0.042503, -0.192152,  0.103608, -0.043752,
                -0.101254,  1.423033, -0.298255, -0.074334],
               [-0.095472, -0.131477,  0.296828, -0.089094,  0.215769, -0.091492,
                -0.088171, -0.298255,  0.910274, -0.024663],
               [-0.213979, -0.134314, -0.011661,  0.174269,  0.166648, -0.227673,
                -0.063964, -0.074334, -0.024663,  0.914586]])
        Coordinates:
          * sample_0  (sample_0) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
          * sample_1  (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
            fid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
            iid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'

    Parameters
    ----------
    filepath : str
        Path to the matrix file.
    id_filepath : str, optional
        Path to the file containing family and individual IDs. It defaults to ``None``,
        in which case it will try to be inferred.

    Returns
    -------
    rel : :class:`xarray.DataArray`
        Realized relationship matrix.

    References
    ----------
    .. [1] Read PLINK realized relationship matrix files.
           https://www.cog-genomics.org/plink/2.0/distance
    """

    ft = file_type(filepath)

    if ft == "zstd":
        return _read_rel_zs(filepath, id_filepath)
    elif ft == "bin":
        return _read_rel_bin(filepath, id_filepath)

    return _read_rel(filepath, id_filepath)


def _read_rel(filepath, id_filepath):
    df = _read_id_file(id_filepath, filepath)
    K = _1d_to_2d(_read_rel_file(filepath), df.shape[0])

    return _data_array(K, df)


def _read_rel_bin(filepath, id_filepath):
    from numpy import fromfile, float64

    df = _read_id_file(id_filepath, filepath)
    K = fromfile(filepath, dtype=float64)
    n = df.shape[0]
    K = K.reshape((n, n))

    return _data_array(K, df)


def _read_rel_file(filepath):
    from numpy import float64

    rows = []
    with open(filepath, "r") as f:
        for row in f:
            rows += [float64(v) for v in row.strip().split("\t")]
    return rows


def _read_rel_zs_rows(filepath, chunk_size=8 * 1000 * 1000):
    from zstandard import ZstdDecompressor

    with open(filepath, "rb") as fh:
        ctx = ZstdDecompressor()
        with ctx.stream_reader(fh) as reader:
            over = False
            chunks = []
            rows = []
            while not over:
                have_row = False
                while not have_row:
                    chunk = reader.read(chunk_size)
                    if not chunk:
                        over = True
                        break
                    if b"\n" in chunk:
                        have_row = True
                    chunks.append(chunk)
                (new_rows, semi_row) = _consume_rows(chunks)
                rows += new_rows
                chunks = [semi_row]
    return rows


def _consume_rows(chunks):
    from numpy import float64

    chunk = b"".join(chunks)
    rows = chunk.split(b"\n")
    semi_row = rows[-1]
    rows = [[float64(v) for v in r.split(b"\t")] for r in rows[:-1]]
    return (rows, semi_row)


def _read_rel_zs(filepath, id_filepath):
    df = _read_id_file(id_filepath, filepath)
    rows = _read_rel_zs_rows(filepath)
    K = _1d_to_2d([v for r in rows for v in r], df.shape[0])
    return _data_array(K, df)


def _data_array(K, df):
    from xarray import DataArray

    coords = (df.iloc[:, 1], df.iloc[:, 1])
    K = DataArray(K, dims=["sample_0", "sample_1"], coords=coords)
    K = K.assign_coords(**{"fid": ("sample_0", df.iloc[:, 0])})
    K = K.assign_coords(**{"fid": ("sample_1", df.iloc[:, 0])})

    K = K.assign_coords(**{"iid": ("sample_0", df.iloc[:, 1])})
    K = K.assign_coords(**{"iid": ("sample_1", df.iloc[:, 1])})

    return K


def _read_id_file(id_filepath, filepath):
    from pandas import read_csv

    if filepath.endswith(".gz"):
        basename = filepath[:-3]
    elif filepath.endswith(".bin"):
        basename = filepath[:-4]
    elif filepath.endswith(".zst"):
        basename = filepath[:-4]
    else:
        basename = filepath

    if id_filepath is None:
        id_filepath = basename + ".id"

    return read_csv(id_filepath, sep="\t", header=None, comment="#")


def _1d_to_2d(values, n):
    from numpy import zeros, tril_indices_from, tril

    K = zeros((n, n))
    K[tril_indices_from(K)] = values
    K = K + tril(K, -1).T
    return K
