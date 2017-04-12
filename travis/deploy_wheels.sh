#!/usr/bin/env bash
set -e -x

if ! [ -z ${DOCKER_IMAGE+x} ]; then
    docker run --rm -v `pwd`:/io $DOCKER_IMAGE /bin/bash
    ls
    ls wheelhouse/
    pip install twine
    twine upload ${TRAVIS_BUILD_DIR}/wheelhouse/pandas_plink*.whl \
        -u dhorta -p $PYPI_PASSWORD
fi
