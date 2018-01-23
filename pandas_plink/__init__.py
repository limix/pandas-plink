from __future__ import absolute_import as _

from .read import read_plink
from .testit import test

__version__ = "1.2.22"


def example_file_prefix():
    r"""Data files prefix."""
    import os
    p = __import__('pandas_plink').__path__[0]
    return os.path.join(p, 'test', 'data_files', 'data')


__all__ = [
    "__name__", "__version__", "test", 'example_file_prefix', 'read_plink'
]
