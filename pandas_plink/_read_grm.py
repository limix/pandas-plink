def read_gcta_grm(filepath, id_filepath=None, n_snps_filepath=None, binary=False):
    if binary:
        return _read_gcta_grm_bin(filepath, id_filepath, n_snps_filepath)

    return _read_gcta_grm(filepath, id_filepath)


def _read_gcta_grm(filepath, id_filepath):
    from pandas import read_csv
    from numpy import asarray, tril, zeros
    from xarray import DataArray

    if filepath.endswith(".gz"):
        basename = filepath[:-3]
    else:
        basename = filepath

    if id_filepath is None:
        id_filepath = basename + ".id"

    df = read_csv(filepath, sep="\t", header=None)
    df_id = read_csv(id_filepath, sep="\t", header=None)
    n = int(df.iloc[-1, 0])
    x = asarray(df.iloc[:, 0] - 1, int)
    y = asarray(df.iloc[:, 1] - 1, int)

    K = zeros((n, n))
    K[x, y] = df.iloc[:, 3]
    K = K + tril(K, -1).T
    coords = (df_id.iloc[:, 1], df_id.iloc[:, 1])
    K = DataArray(K, dims=["sample_0", "sample_1"], coords=coords)
    K = K.assign_coords(**{"fid": ("sample_0", df_id.iloc[:, 0])})
    K = K.assign_coords(**{"fid": ("sample_1", df_id.iloc[:, 0])})

    K = K.assign_coords(**{"iid": ("sample_0", df_id.iloc[:, 1])})
    K = K.assign_coords(**{"iid": ("sample_1", df_id.iloc[:, 1])})

    n_snps = asarray(df.iloc[:, 2], int)

    return (K, n_snps)


def _read_gcta_grm_bin(filepath, id_filepath, n_snps_filepath):
    from pandas import read_csv
    from numpy import asarray, tril, zeros, float32, fromfile, tril_indices_from
    from xarray import DataArray

    if id_filepath is None:
        id_filepath = _last_replace(filepath, ".bin", ".id")

    if n_snps_filepath is None:
        n_snps_filepath = _last_replace(filepath, ".bin", ".N.bin")

    df_id = read_csv(id_filepath, sep="\t", header=None)
    n = df_id.shape[0]
    k = asarray(fromfile(filepath, dtype=float32), float)
    n_snps = asarray(fromfile(n_snps_filepath, dtype=float32), float)

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


def _last_replace(s, old, new):
    li = s.rsplit(old, 1)
    return new.join(li)
