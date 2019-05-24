def read_rel(filepath, id_filepath=None, binary=False):
    if binary:
        return _read_rel_bin(filepath, id_filepath)

    return _read_rel(filepath, id_filepath)


def _read_rel(filepath, id_filepath):
    from numpy import tril, zeros, tril_indices_from

    if filepath.endswith(".gz"):
        basename = filepath[:-3]
    else:
        basename = filepath

    if id_filepath is None:
        id_filepath = basename + ".id"

    df = _read_id_file(id_filepath)
    n = df.shape[0]

    rows = _read_rel_file(filepath)
    K = zeros((n, n))
    K[tril_indices_from(K)] = rows
    K = K + tril(K, -1).T

    return _data_array(K, df)


def _read_rel_bin(filepath, id_filepath):
    from numpy import fromfile, float64

    if filepath.endswith(".gz"):
        basename = filepath[:-3]
    elif filepath.endswith(".bin"):
        basename = filepath[:-4]
    else:
        basename = filepath

    if id_filepath is None:
        id_filepath = basename + ".id"

    df = _read_id_file(id_filepath)
    K = fromfile(filepath, dtype=float64)
    n = df.shape[0]
    K = K.reshape((n, n))

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


def _read_rel_file(filepath):
    rows = []
    with open(filepath, "r") as f:
        for row in f:
            rows += [float(v) for v in row.strip().split("\t")]
    return rows


def _read_id_file(filepath):
    from pandas import read_csv

    return read_csv(filepath, sep="\t", header=None, comment="#")
