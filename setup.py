import os
import sys

from setuptools import find_packages, setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except (OSError, IOError, ImportError):
    long_description = open('README.md').read()


def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []

    setup_requires = ['cffi>=1.7'] + pytest_runner
    install_requires = ['pandas>=0.17', 'cffi>=1.7',
                        'numpy>=1.9', 'dask[complete]>=0.13', 'toolz>=0.8']
    tests_require = ['pytest']

    metadata = dict(
        name='pandas-plink',
        version='1.1.3',
        maintainer="Danilo Horta",
        maintainer_email="horta@ebi.ac.uk",
        description="Read PLINK files into Pandas data frames.",
        long_description=long_description,
        license="MIT",
        url='https://github.com/glimix/pandas-plink',
        packages=find_packages(),
        zip_safe=False,
        install_requires=install_requires,
        setup_requires=setup_requires,
        tests_require=tests_require,
        include_package_data=True,
        package_data={
            '': [os.path.join('pandas_link', 'test', 'data_files', '*.*')]
        },
        cffi_modules=["pandas_plink/builder.py:ffibuilder"],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Operating System :: OS Independent",
        ], )

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)


if __name__ == '__main__':
    setup_package()
