def file_type(filepath):

    if _is_gzip(filepath):
        file_type = "gzip"
    elif _is_zstd(filepath):
        file_type = "zstd"
    elif _is_binary_file(filepath):
        file_type = "bin"
    else:
        file_type = "txt"

    return file_type


def _is_zstd(filepath):
    with open(filepath, "rb") as f:
        hdr = f.read(4)
        if int.from_bytes(hdr, byteorder="little") == 4247762216:
            return True
    return False


def _is_gzip(filepath):
    with open(filepath, "rb") as f:
        hdr = f.read(2)
        if int.from_bytes(hdr, byteorder="little") == 35615:
            return True
    return False


def _is_binary_file(filepath):
    with open(filepath, "rb") as f:
        bytes = f.read(1024)
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    return bool(bytes.translate(None, textchars))
