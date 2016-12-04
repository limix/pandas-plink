import os
import sys

from setuptools import find_packages
from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []

    setup_requires = ['cffi>=1.0.0'] + pytest_runner
    install_requires = ['pandas>=0.19', 'cffi>=1.0.0']
    tests_require = ['pytest', 'pytest-datafiles', 'numpy>=1.9']

    metadata = dict(
        name='pandas_plink',
        version='1.0.0.dev2',
        maintainer="Danilo Horta",
        maintainer_email="horta@ebi.ac.uk",
        description="Read PLINK files into Pandas data frames.",
        long_description=long_description,
        license="MIT",
        url='https://github.com/Horta/optimix',
        packages=find_packages(),
        zip_safe=True,
        install_requires=install_requires,
        setup_requires=setup_requires,
        tests_require=tests_require,
        include_package_data=True,
        cffi_modules=["bed_reader_build.py:ffibuilder"],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Operating System :: OS Independent",
        ],
    )

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)

if __name__ == '__main__':
    setup_package()
