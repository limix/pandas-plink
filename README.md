# pandas-plink

[![linux / macos build](https://img.shields.io/travis/limix/pandas-plink/master.svg?label=linux%20%2F%20macos&style=flat-square)](https://travis-ci.org/limix/pandas-plink) [![windows build](https://img.shields.io/appveyor/ci/horta/pandas-plink/master.svg?label=windows&style=flat-square)](https://ci.appveyor.com/project/Horta/pandas-plink/branch/master) [![PyPI-Version](https://img.shields.io/pypi/v/pandas-plink.svg?style=flat-square&label=pypi)](https://img.shields.io/pypi/v/pandas-plink.svg) [![Conda-Version](https://img.shields.io/conda/vn/conda-forge/pandas-plink.svg?style=flat-square&label=conda-forge)](https://img.shields.io/conda/vn/conda-forge/pandas-plink.svg)
[![License](https://img.shields.io/pypi/l/pandas-plink.svg?style=flat-square)](https://raw.githubusercontent.com/limix/pandas-plink/master/LICENSE.txt) [![Codacy grade](https://img.shields.io/codacy/grade/279d016293724b79ad8e667c1440d3d0.svg?style=flat-square)](https://www.codacy.com/app/danilo.horta/pandas-plink?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=limix/pandas-plink&amp;utm_campaign=Badge_Grade) [![Documentation](https://img.shields.io/readthedocs/pandas-plink.svg?style=flat-square&version=stable)](https://pandas-plink.readthedocs.io/) [![Gitter](https://img.shields.io/gitter/room/limix/pandas-plink.js.svg?style=flat-square)](https://gitter.im/pandas-plink/Lobby)

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
