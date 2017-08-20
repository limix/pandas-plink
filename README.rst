pandas-plink
============

|PyPI-Status| |Conda-Forge-Status| |Conda-Downloads|

|Build-Status| |Codacy-Grade| |License-Badge| |Doc-Status|

PLINK reader for Python.
It reads binary PLINK files into Pandas_ data frame and Dask_ array.
This package handles larger-than-memory data sets by reading the SNP matrix
on-demand.

Install
-------

The recommended way of installing it is via conda_

.. code:: bash

    conda install -c conda-forge pandas-plink

An alternative way would be via pip_

.. code:: bash

    pip install pandas-plink

Running the tests
-----------------

After installation, you can test it

.. code:: bash

    python -c "import pandas_plink; pandas_plink.test()"

as long as you have pytest_.

Usage
-----

It is as simple as

.. code:: python

    from pandas_plink import read_plink
    (bim, fam, G) = read_plink('/path/to/data')

Refer to the documentation_ for more information.

Authors
-------

* `Danilo Horta`_

License
-------

This project is licensed under the MIT License - see the `License file`_ file
for details.

.. |Build-Status| image:: https://travis-ci.org/limix/pandas-plink.svg?branch=master
    :target: https://travis-ci.org/limix/pandas-plink

.. |Codacy-Grade| image:: https://api.codacy.com/project/badge/Grade/279d016293724b79ad8e667c1440d3d0
    :target: https://www.codacy.com/app/danilo.horta/pandas-plink?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=limix/pandas-plink&amp;utm_campaign=Badge_Grade

.. |PyPI-Status| image:: https://img.shields.io/pypi/v/pandas-plink.svg
    :target: https://pypi.python.org/pypi/pandas-plink

.. |PyPI-Versions| image:: https://img.shields.io/pypi/pyversions/pandas-plink.svg
    :target: https://pypi.python.org/pypi/pandas-plink

.. |Conda-Forge-Status| image:: https://anaconda.org/conda-forge/pandas-plink/badges/version.svg
    :target: https://anaconda.org/conda-forge/pandas-plink

.. |Conda-Downloads| image:: https://anaconda.org/conda-forge/pandas-plink/badges/downloads.svg
    :target: https://anaconda.org/conda-forge/pandas-plink

.. |License-Badge| image:: https://img.shields.io/pypi/l/pandas-plink.svg
    :target: https://raw.githubusercontent.com/limix/pandas-plink/master/LICENSE.txt

.. |Doc-Status| image:: https://readthedocs.org/projects/pandas-plink/badge/?style=flat-square&version=stable
    :target: https://pandas-plink.readthedocs.io/

.. _License file: https://raw.githubusercontent.com/limix/pandas-plink/master/LICENSE.txt

.. _Danilo Horta: https://github.com/horta

.. _conda: http://conda.pydata.org/docs/index.html

.. _pip: https://pypi.python.org/pypi/pip

.. _pytest: http://docs.pytest.org/en/latest/

.. _Dask: http://dask.pydata.org/en/latest/index.html

.. _Pandas: http://pandas.pydata.org

.. _documentation: http://pandas-plink.readthedocs.io/
