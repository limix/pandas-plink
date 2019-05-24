from ._filetype import file_type


def read_rel(filepath, id_filepath=None):
    """
    Read PLINK realized relationship matrix files.

    It supports plain text, binary, and compressed files.

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
    rows = []
    with open(filepath, "r") as f:
        for row in f:
            rows += [float(v) for v in row.strip().split("\t")]
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
    chunk = b"".join(chunks)
    rows = chunk.split(b"\n")
    semi_row = rows[-1]
    rows = [[float(v) for v in r.split(b"\t")] for r in rows[:-1]]
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
