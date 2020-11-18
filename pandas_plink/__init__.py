from ._chunk import Chunk
from ._data import example_file_prefix, get_data_folder
from ._read import read_plink, read_plink1_bin
from ._read_grm import read_grm
from ._read_rel import read_rel
from ._testit import test
from ._write import write_plink1_bin

__version__ = "2.2.3"


__all__ = [
    "Chunk",
    "__version__",
    "example_file_prefix",
    "get_data_folder",
    "read_grm",
    "read_plink",
    "read_plink1_bin",
    "read_rel",
    "test",
    "write_plink1_bin",
]
