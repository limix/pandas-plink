from deprecated.sphinx import deprecated


@deprecated(reason="use function :func:`get_data_folder` instead.", version="2.0.0")
def example_file_prefix():
    """
    Data files prefix.
    """
    import os

    p = __import__("pandas_plink").__path__[0]
    return os.path.join(p, "test", "data_files", "data")


def get_data_folder():
    """
    Path to the folder containing example files.
    """
    import os

    p = __import__("pandas_plink").__path__[0]
    return os.path.join(p, "test", "data_files")
