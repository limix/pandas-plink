============================
Pandas-plink's documentation
============================

Read PLINK files into Pandas data frames with support of mapping multiple BED
files at once.

*******
Install
*******

It can be installed via pip::

  pip install pandas-plink

Or via `conda`_::

  conda install -c conda-forge pandas-plink

.. _conda: http://conda.pydata.org/docs/index.html

*****
Usage
*****

It is as simple as::

  from pandas_plink import read_plink
  (bim, fam, G) = read_plink('/path/to/data')

assuming that you have the files

  - `/path/to/data.bim`
  - `/path/to/data.fam`
  - `/path/to/data.bed`

The returned matrix ``G`` contains ``0``, ``1``, ``2``, or ``NaN``:

- ``0`` Homozygous having the first allele (column ``a0`` of ``bim``)
- ``1`` Heterozygous
- ``2`` Homozygous having the second allele (column ``a1`` of ``bim``)
- ``NaN`` Missing genotype

The matrix ``G`` is a `Dask`_ array instead of an usual `NumPy`_ array.
It allows for lazy-loading large datasets that would not be able to fit
in memory.

.. _Dask: https://dask.pydata.org/
.. _NumPy: http://www.numpy.org

*********
Functions
*********

.. automodule:: pandas_plink

  .. autofunction:: example_file_prefix
  .. autofunction:: get_data_folder
  .. autofunction:: read_gcta_grm
  .. autofunction:: read_plink
  .. autofunction:: read_plink1_bin
  .. autofunction:: read_rel
  .. autofunction:: test
