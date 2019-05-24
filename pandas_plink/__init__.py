from ._read import read_plink, read_plink1_bin
from ._read_grm import read_gcta_grm
from ._read_rel import read_rel
from ._testit import test
from ._data import example_file_prefix, get_data_folder

__version__ = "2.0.0"


__all__ = [
    "__version__",
    "test",
    "example_file_prefix",
    "read_plink",
    "read_plink1_bin",
    "read_gcta_grm",
    "read_rel",
    "get_data_folder",
]
