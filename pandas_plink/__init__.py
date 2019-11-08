from ._data import example_file_prefix, get_data_folder
from ._read import read_plink, read_plink1_bin
from ._read_grm import read_grm
from ._read_rel import read_rel
from ._testit import test

__version__ = "2.0.3"


__all__ = [
    "__version__",
    "test",
    "example_file_prefix",
    "read_plink",
    "read_plink1_bin",
    "read_grm",
    "read_rel",
    "get_data_folder",
]
