# pandas-plink

[![PyPIl](https://img.shields.io/pypi/l/pandas-plink.svg?style=flat-square)](https://pypi.python.org/pypi/pandas-plink/)
[![PyPIv](https://img.shields.io/pypi/v/pandas-plink.svg?style=flat-square)](https://pypi.python.org/pypi/pandas-plink/)
[![Documentation Status](https://readthedocs.org/projects/pandas-plink/badge/?style=flat-square&version=latest)](https://pandas-plink.readthedocs.io/en/latest/)

Convert PLINK files to Pandas data frame.

## Install

The recommended way of installing it is via
[conda](http://conda.pydata.org/docs/index.html)

```bash
conda install -c conda-forge pandas-plink
```

An alternative way would be via pip

```
pip install pandas-plink
```

## Running the tests

After installation, you can test it
```
python -c "import pandas_plink; pandas_plink.test()"
```
as long as you have [pytest](http://docs.pytest.org/en/latest/).

## Usage

It is as simple as

```python
from pandas_plink import read_plink
(bim, fam, G) = read_plink('/path/to/data')
```

Refer to [documentation](http://pandas-plink.readthedocs.io/en/latest/)
for more information.

## Authors

* **Danilo Horta** - [https://github.com/Horta](https://github.com/Horta)

## License

This project is licensed under the MIT License - see the
[LICENSE](LICENSE) file for details
