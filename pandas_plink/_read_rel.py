def read_rel(filepath, id_filepath=None, binary=False):
    if binary:
        return _read_rel_bin(filepath, id_filepath)

    return _read_rel(filepath, id_filepath)


def _read_rel(filepath, id_filepath):
    from pandas import read_csv
    from numpy import tril, zeros, tril_indices_from
    from xarray import DataArray

    if filepath.endswith(".gz"):
        basename = filepath[:-3]
    else:
        basename = filepath

    if id_filepath is None:
        id_filepath = basename + ".id"

    df_id = read_csv(id_filepath, sep="\t", header=None)
    n = df_id.shape[0]

    rows = _read_rel_file(filepath)
    K = zeros((n, n))
    K[tril_indices_from(K)] = rows
    K = K + tril(K, -1).T

    coords = (df_id.iloc[:, 1], df_id.iloc[:, 1])
    K = DataArray(K, dims=["sample_0", "sample_1"], coords=coords)
    K = K.assign_coords(**{"fid": ("sample_0", df_id.iloc[:, 0])})
    K = K.assign_coords(**{"fid": ("sample_1", df_id.iloc[:, 0])})

    K = K.assign_coords(**{"iid": ("sample_0", df_id.iloc[:, 1])})
    K = K.assign_coords(**{"iid": ("sample_1", df_id.iloc[:, 1])})

    return K


def _read_rel_file(filepath):
    rows = []
    with open(filepath, "r") as f:
        for row in f:
            rows += [float(v) for v in row.strip().split("\t")]
    return rows
