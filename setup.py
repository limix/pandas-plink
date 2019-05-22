from setuptools import setup

if __name__ == "__main__":
    setup(cffi_modules="pandas_plink/_builder.py:ffibuilder")
