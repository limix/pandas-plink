from __future__ import unicode_literals

import os

import pytest


def pytest_configure(*_):
    _compatibility()
    import doctest

    pandas_format()
    doctest.ELLIPSIS_MARKER = "-ignore-"


@pytest.fixture(autouse=True)
def _docdir(request):

    # Trigger ONLY for the doctests.
    doctest_plugin = request.config.pluginmanager.getplugin("doctest")
    if isinstance(request.node, doctest_plugin.DoctestItem):

        # Get the fixture dynamically by its name.
        # tmpdir = request.getfuncargvalue("tmpdir")
        tmpdir = request.getfixturevalue("tmpdir")

        # Chdir only for the duration of the test.
        olddir = os.getcwd()
        tmpdir.chdir()
        yield
        os.chdir(olddir)

    else:
        # For normal tests, we have to yield, since this is a yield-fixture.
        yield


def pandas_format():
    import pandas as pd

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 79)
    pd.set_option("display.max_rows", 60)
    pd.set_option("display.large_repr", "truncate")


def _compatibility():
    import warnings

    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
