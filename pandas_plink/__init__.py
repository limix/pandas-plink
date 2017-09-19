from __future__ import absolute_import as _

import _cffi_backend

from ._test import test
from .read import read_plink

__name__ = "pandas-plink"
__version__ = "1.2.13"
__author__ = "Danilo Horta"
__author_email__ = "horta@ebi.ac.uk"


def example_file_prefix():
    r"""Data files prefix."""
    import os
    p = __import__('pandas_plink').__path__[0]
    return os.path.join(p, 'test', 'data_files', 'data')


__all__ = [
    "__name__", "__version__", "__author__", "__author_email__", "test",
    'example_file_prefix', 'read_plink'
]
