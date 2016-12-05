# pandas-plink

[![PyPIl](https://img.shields.io/pypi/l/pandas_plink.svg?style=flat-square)](https://pypi.python.org/pypi/pandas_plink/)
[![PyPIv](https://img.shields.io/pypi/v/pandas_plink.svg?style=flat-square)](https://pypi.python.org/pypi/pandas_plink/)
[![Documentation Status](https://readthedocs.org/projects/pandas_plink/badge/?style=flat-square&version=latest)](http://pandas_plink.readthedocs.io/en/latest/?badge=latest)

<!-- [![Anaconda-Server Badge](https://anaconda.org/conda-forge/pandas_plink/badges/version.svg)](https://anaconda.org/conda-forge/pandas_plink) -->

Convert plink files to Pandas data frame.

## Install

You can install via pip
```bash
pip install pandas_plink
```

<!-- The recommended way of installing it is via
[conda](http://conda.pydata.org/docs/index.html)
```bash
conda install -c conda-forge pandas_plink
``` -->

<!-- An alternative way would be via pip
```bash
pip install pandas_plink
``` -->

## Running the tests

After installation, you can test it
```
python -c "import pandas_plink; pandas_plink.test()"
```
as long as you have [pytest](http://docs.pytest.org/en/latest/) and
[pytest-datafiles](https://pypi.python.org/pypi/pytest-datafiles).

## Usage

It is as simple as

```
from pandas_plink import read_plink
(bim, fam, G) = read_plink('/path/to/data')
```

assuming you have the files `/path/to/data.[bim|fam|bed]`.

## Authors

* **Danilo Horta** - [https://github.com/Horta](https://github.com/Horta)

## License

This project is licensed under the MIT License - see the
[LICENSE](LICENSE) file for details
