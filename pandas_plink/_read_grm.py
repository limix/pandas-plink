def read_gcta_grm(grm_filepath, grm_id_filepath=None, binary=False):
    from pandas import read_csv
    from numpy import asarray, tril, zeros
    from xarray import DataArray

    if grm_id_filepath is None:
        grm_id_filepath = grm_filepath + ".id"

    df = read_csv(grm_filepath, sep="\t", header=None)
    df_id = read_csv(grm_id_filepath, sep="\t", header=None)
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
