# pandas-plink

[![Travis](https://img.shields.io/travis/limix/pandas-plink.svg?style=flat-square&label=linux%20%2F%20macos%20build)](https://travis-ci.org/limix/pandas-plink) [![AppVeyor](https://img.shields.io/appveyor/ci/Horta/pandas-plink.svg?style=flat-square&label=windows%20build)](https://ci.appveyor.com/project/Horta/pandas-plink) [![Documentation](https://img.shields.io/readthedocs/pandas-plink.svg?style=flat-square&version=stable)](https://pandas-plink.readthedocs.io/)

Pandas-plink is a Python package for reading [PLINK binary file format](https://www.cog-genomics.org/plink2/formats).
The file reading is taken place via [lazy loading](https://en.wikipedia.org/wiki/Lazy_loading), meaning that it saves up memory by actually reading only the genotypes that are actually accessed by the user.

## Install

We recommend installing it via [conda](http://conda.pydata.org/docs/index.html):

```bash
conda install -c conda-forge pandas-plink
```

The above method is preferable because it does not require building tools, which makes the installation less prone to errors.

Alternatively, pandas-plink can also be installed using [pip](https://pypi.python.org/pypi/pip):

```bash
pip install pandas-plink
```

The above method will perform some compilation and the installation is very likely to be successful, as we test every release under Windows, Linux, and macOS platforms.
If by any change it fails, please, consider submitting a [new issue](https://github.com/limix/pandas-plink/issues/new).

## Usage

It is as simple as

```python
from pandas_plink import read_plink
(bim, fam, G) = read_plink('/path/to/files_prefix')
```

for which `files_prefix.bed`, `files_prefix.bim`, and `files_prefix.fam` contain the data.
Portions of the genotype will be read as the user access them. Please, refer to the [documentation](https://pandas-plink.readthedocs.io/) for more information.

## Authors

* [Danilo Horta](https://github.com/horta)

## License

This project is licensed under the [MIT License](https://raw.githubusercontent.com/limix/pandas-plink/master/LICENSE.md).
