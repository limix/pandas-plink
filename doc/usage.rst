*****
Usage
*****

It is as simple as::

.. testsetup:: *

  >>> from os.path import join
  >>> from pandas_plink import get_data_folder
  >>> from shutil import copy
  >>> filenames = ["chr11.bed", "chr11.bim", "chr11.fam", "chr12.bed", "chr12.bim",
  ...              "chr12.fam"]
  >>> for f in filenames:
  ...     _ = copy(join(get_data_folder(), f), ".")

.. doctest::

  >>> from pandas_plink import read_plink1_bin
  >>> G = read_plink1_bin("chr11.bed", "chr11.bim", "chr11.fam", verbose=False)
  >>> print(G)
  <xarray.DataArray 'genotype' (sample: 14, variant: 779)>
  dask.array<shape=(14, 779), dtype=float64, chunksize=(14, 779)>
  Coordinates:
    * sample   (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
    * variant  (variant) object '11_316849996' '11_316874359' ... '11_345698259'
      father   (sample) <U1 '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
      fid      (sample) <U4 'B001' 'B002' 'B003' 'B004' ... 'B012' 'B013' 'B014'
      gender   (sample) <U1 '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
      i        (sample) int64 0 1 2 3 4 5 6 7 8 9 10 11 12 13
      iid      (sample) <U4 'B001' 'B002' 'B003' 'B004' ... 'B012' 'B013' 'B014'
      mother   (sample) <U1 '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
      trait    (sample) <U2 '-9' '-9' '-9' '-9' '-9' ... '-9' '-9' '-9' '-9' '-9'
      a0       (variant) <U1 'C' 'G' 'G' 'C' 'C' 'T' ... 'T' 'A' 'C' 'A' 'A' 'T'
      a1       (variant) <U1 'T' 'C' 'C' 'T' 'T' 'A' ... 'C' 'G' 'T' 'G' 'C' 'C'
      chrom    (variant) <U2 '11' '11' '11' '11' '11' ... '11' '11' '11' '11' '11'
      cm       (variant) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0
      pos      (variant) int64 157439 181802 248969 ... 28937375 28961091 29005702
      snp      (variant) <U9 '316849996' '316874359' ... '345653648' '345698259'

The returned matrix ``G`` contains ``0``, ``1``, ``2``, or ``NaN``:

- ``0`` Homozygous having the first allele (column ``a0`` of ``bim``)
- ``1`` Heterozygous
- ``2`` Homozygous having the second allele (column ``a1`` of ``bim``)
- ``NaN`` Missing genotype

The matrix ``G`` is a `Dask`_ array instead of an usual `NumPy`_ array.
It allows for lazy-loading large datasets that would not be able to fit
in memory.

.. testcleanup::

  >>> import os
  >>> if os.path.basename(os.getcwd()) != "data_files":
  ...     for f in filenames:
  ...         os.remove(f)


.. _Dask: https://dask.pydata.org/
.. _NumPy: http://www.numpy.org
