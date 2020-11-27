*****
Usage
*****

Genotype
========

It is as simple as:

.. testsetup::

    >>> from os.path import join
    >>> from pandas_plink import get_data_folder
    >>> from shutil import copy
    >>> filenames = ["chr11.bed", "chr11.bim", "chr11.fam", "chr12.bed", "chr12.bim",
    ...              "chr12.fam"]
    >>> for f in filenames:
    ...     _ = copy(join(get_data_folder(), f), ".")
    >>> rel_filenames = ["plink2.rel.bin", "plink2.rel.id"]
    >>> for f in rel_filenames:
    ...     _ = copy(join(get_data_folder(), "rel-bin", f), ".")

.. doctest::

    >>> from pandas_plink import read_plink1_bin
    >>> G = read_plink1_bin("chr11.bed", "chr11.bim", "chr11.fam", verbose=False)
    >>> print(G)
    <xarray.DataArray 'genotype' (sample: 14, variant: 779)>
    dask.array<transpose, shape=(14, 779), dtype=float32, chunksize=(14, 779), chunktype=numpy.ndarray>
    Coordinates:
      * sample   (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
      * variant  (variant) <U10 'variant0' 'variant1' ... 'variant777' 'variant778'
        fid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
        iid      (sample) object 'B001' 'B002' 'B003' ... 'B012' 'B013' 'B014'
        father   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
        mother   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
        gender   (sample) object '0' '0' '0' '0' '0' '0' ... '0' '0' '0' '0' '0' '0'
        trait    (sample) object '-9' '-9' '-9' '-9' '-9' ... '-9' '-9' '-9' '-9'
        chrom    (variant) object '11' '11' '11' '11' '11' ... '11' '11' '11' '11'
        snp      (variant) object '316849996' '316874359' ... '345698259'
        cm       (variant) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0
        pos      (variant) int32 157439 181802 248969 ... 28937375 28961091 29005702
        a0       (variant) object 'C' 'G' 'G' 'C' 'C' 'T' ... 'A' 'C' 'A' 'A' 'T'
        a1       (variant) object 'T' 'C' 'C' 'T' 'T' 'A' ... 'G' 'T' 'G' 'C' 'C'

The matrix :py:`G` is a special matrix: :class:`xarray.DataArray`. It provides labes for its
dimensions (`"sample"` for rows and `"variant"` for columns) and additional metadata for
those dimensions.
Lets print the genotype value of sample `B003` and variant `variant5`:

.. doctest::

    >>> variant = "variant5"
    >>> print(G.sel(sample="B003", variant=variant).values)
    0.0
    >>> print(G.a0.sel(variant=variant).values)
    T

It means that sample `B003` has two alleles `T` at the variant `variant5`.
Likewise, sample `B003` has two alleles `C` at the variant `variant135`:

.. doctest::

    >>> variant = "variant135"
    >>> print(G.sel(sample="B003", variant=variant).values)
    2.0
    >>> print(G.a1.sel(variant=variant).values)
    C

Now lets print a summary of the genotype values:

.. doctest::

    >>> print(G.values)
    [[0.00 0.00 2.00 ... 0.00 0.00 0.00]
     [0.00 1.00 2.00 ... 0.00 0.00  nan]
     [0.00 0.00 2.00 ... 0.00 0.00 0.00]
     ...
     [2.00 2.00 0.00 ... 2.00 2.00 2.00]
     [2.00 1.00 0.00 ... 2.00 2.00 1.00]
     [0.00 0.00 2.00 ... 0.00 0.00  nan]]


The genotype values can be either ``0``, ``1``, ``2``, or ``NaN``:

- ``0`` Homozygous having the first allele (given by coordinate ``a0``)
- ``1`` Heterozygous
- ``2`` Homozygous having the second allele (given by coordinate ``a1``)
- ``NaN`` Missing genotype


Kinship matrix
==============

Pandas-plink supports relationship/covariance matrix encoded in PLINK and GCTA file
formats since version 2.0.0.

.. doctest::

    >>> from pandas_plink import read_rel
    >>> K = read_rel("plink2.rel.bin")
    >>> print(K)
    <xarray.DataArray (sample_0: 10, sample_1: 10)>
    array([[ 0.89,  0.23, -0.19, -0.01, -0.14,  0.29,  0.27, -0.23, -0.10,
            -0.21],
           [ 0.23,  1.08, -0.45,  0.19, -0.19,  0.17,  0.41, -0.01, -0.13,
            -0.13],
           [-0.19, -0.45,  1.18, -0.04, -0.15, -0.20, -0.31, -0.04,  0.30,
            -0.01],
           [-0.01,  0.19, -0.04,  0.90, -0.07,  0.01,  0.06, -0.19, -0.09,
             0.17],
           [-0.14, -0.19, -0.15, -0.07,  1.18,  0.09, -0.03,  0.10,  0.22,
             0.17],
           [ 0.29,  0.17, -0.20,  0.01,  0.09,  0.96,  0.07, -0.04, -0.09,
            -0.23],
           [ 0.27,  0.41, -0.31,  0.06, -0.03,  0.07,  0.71, -0.10, -0.09,
            -0.06],
           [-0.23, -0.01, -0.04, -0.19,  0.10, -0.04, -0.10,  1.42, -0.30,
            -0.07],
           [-0.10, -0.13,  0.30, -0.09,  0.22, -0.09, -0.09, -0.30,  0.91,
            -0.02],
           [-0.21, -0.13, -0.01,  0.17,  0.17, -0.23, -0.06, -0.07, -0.02,
             0.91]])
    Coordinates:
      * sample_0  (sample_0) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
      * sample_1  (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
        fid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
        iid       (sample_1) object 'HG00419' 'HG00650' ... 'NA20508' 'NA20753'
    >>> print(K.values)
    [[ 0.89  0.23 -0.19 -0.01 -0.14  0.29  0.27 -0.23 -0.10 -0.21]
     [ 0.23  1.08 -0.45  0.19 -0.19  0.17  0.41 -0.01 -0.13 -0.13]
     [-0.19 -0.45  1.18 -0.04 -0.15 -0.20 -0.31 -0.04  0.30 -0.01]
     [-0.01  0.19 -0.04  0.90 -0.07  0.01  0.06 -0.19 -0.09  0.17]
     [-0.14 -0.19 -0.15 -0.07  1.18  0.09 -0.03  0.10  0.22  0.17]
     [ 0.29  0.17 -0.20  0.01  0.09  0.96  0.07 -0.04 -0.09 -0.23]
     [ 0.27  0.41 -0.31  0.06 -0.03  0.07  0.71 -0.10 -0.09 -0.06]
     [-0.23 -0.01 -0.04 -0.19  0.10 -0.04 -0.10  1.42 -0.30 -0.07]
     [-0.10 -0.13  0.30 -0.09  0.22 -0.09 -0.09 -0.30  0.91 -0.02]
     [-0.21 -0.13 -0.01  0.17  0.17 -0.23 -0.06 -0.07 -0.02  0.91]]

.. testcleanup::

    >>> import os
    >>> if os.path.basename(os.getcwd()) != "data_files":
    ...     for f in filenames:
    ...         os.remove(f)
    >>> if os.path.basename(os.getcwd()) != "data_files":
    ...     for f in rel_filenames:
    ...         os.remove(f)

Please, refer to the functions :func:`pandas_plink.read_rel` and
:func:`pandas_plink.read_grm` for more details.
