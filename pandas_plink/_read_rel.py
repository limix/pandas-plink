def read_rel(filepath, id_filepath=None):
    import magic

    info = magic.from_file(filepath)
    if info.startswith("Zstandard"):
        return _read_rel_zs(filepath, id_filepath)

    if info.startswith("data"):
        return _read_rel_bin(filepath, id_filepath)

    return _read_rel(filepath, id_filepath)


def _read_rel(filepath, id_filepath):
    from numpy import tril, zeros, tril_indices_from

    df = _read_id_file(id_filepath, filepath)
    n = df.shape[0]

    rows = _read_rel_file(filepath)
    K = zeros((n, n))
    K[tril_indices_from(K)] = rows
    K = K + tril(K, -1).T

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
    from numpy import zeros, tril_indices_from, tril

    df = _read_id_file(id_filepath, filepath)
    n = df.shape[0]

    rows = _read_rel_zs_rows(filepath)
    flat = [v for r in rows for v in r]
    K = zeros((n, n))
    K[tril_indices_from(K)] = flat
    K = K + tril(K, -1).T

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


def _file_type(filepath):

    file_type = "txt"
    try:
        import magic

        info = magic.from_file(filepath)
        if info.startswith("Zstandard"):
            file_type = "zstd"
        elif info.startswith("data"):
            file_type = _binary_zstd(filepath)

    except ImportError:
        if _is_binary_file(filepath):
            file_type = _binary_zstd(filepath)

    return file_type


def _binary_zstd(filepath):
    file_type = "bin"
    with open(filepath, "rb") as f:
        hdr = f.read(4)
        if int.from_bytes(hdr, byteorder="little") == 4247762216:
            file_type = "zstd"
        else:
            file_type = "bin"
    return file_type


def _is_binary_file(filepath):
    with open(filepath, "rb") as f:
        bytes = f.read(1024)
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    return bool(bytes.translate(None, textchars))
