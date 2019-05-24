def file_type(filepath):

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
