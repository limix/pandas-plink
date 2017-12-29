# pandas-plink

[![Linux / macOS build](https://img.shields.io/travis/limix/pandas-plink/master.svg?label=Linux%20%2F%20macOS&style=flat-square)](https://travis-ci.org/limix/pandas-plink) [![Windows build](https://img.shields.io/appveyor/ci/horta/pandas-plink/master.svg?label=Windows&style=flat-square)](https://ci.appveyor.com/project/Horta/pandas-plink/branch/master)

[![adkslkda](https://img.shields.io/pypi/v/nine.svg?style=flat-square&label=pypi)](https://img.shields.io/pypi/v/pandas-plink.svg) [![dqwdq](https://img.shields.io/conda/vn/conda-forge/python.svg?style=flat-square&label=conda-forge)](https://img.shields.io/conda/vn/conda-forge/python.svg)

## Install

We recommend installing it via [conda](http://conda.pydata.org/docs/index.html):

```bash
conda install -c conda-forge pandas-plink
```

Alternatively, the installation using [pip](https://pypi.python.org/pypi/pip) should work fine as well:

```bash
pip install pandas-plink
```

## Usage

It is as simple as
```python
from pandas_plink import read_plink
(bim, fam, G) = read_plink('/path/to/files_prefix')
```
for which `files_prefix.bed`, `files_prefix.bim`, and `files_prefix.fam` contain
the data.

Please, refer to the [documentation](https://pandas-plink.readthedocs.io/) for more information.

## Authors

* [Danilo Horta](https://github.com/horta)

## License

This project is licensed under the [MIT License](https://raw.githubusercontent.com/limix/pandas-plink/master/LICENSE.txt).
