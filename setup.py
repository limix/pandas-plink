#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup(cffi_modules="build_ext.py:ffibuilder")
