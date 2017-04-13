#!/usr/bin/env bash
set -e -x

if [ -z ${DOCKER_IMAGE+x} ]; then

    if [[ $TRAVIS_OS_NAME == 'linux' ]]; then
        python setup.py sdist
        pip install dist/`ls dist | grep -i -E '\.(gz)$' | head -1`;
        pushd /
        python -c "import sys; import pandas_plink; sys.exit(pandas_plink.test())"
        popd
    else
        pip install --upgrade pip
        pip install wheel setuptools
        python setup.py bdist_wheel
        ls dist
    fi
else
    docker run --rm -v `pwd`:/io $DOCKER_IMAGE /io/travis/build_wheels.sh
    ls wheelhouse/
fi
