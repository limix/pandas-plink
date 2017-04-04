============================
Pandas-plink's documentation
============================

You can get the source and open issues on `Github.`_

.. _Github.: https://github.com/glimix/pandas-plink

*******
Install
*******

The recommended way of installing it is via `conda`_::

  conda install -c conda-forge pandas-plink

An alternative way would be via pip::

  pip install pandas-plink

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

The returned matrix ``G`` contains 0, 1, 2, or 3s:

- 0 Homozygous for first allele in .bim file
- 1 Heterozygous
- 2 Homozygous for second allele in .bim file
- 3 Missing genotype


*********
Functions
*********

.. automodule:: pandas_plink

  .. autofunction:: read_plink
  .. autofunction:: test
  .. autofunction:: example_file_prefix
