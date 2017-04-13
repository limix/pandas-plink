#!/bin/bash

set -e

if ! [ -z ${DOCKER_IMAGE+x} ]; then
    if [[ $TRAVIS_OS_NAME == 'linux' ]]; then
        docker run -e PYPI_PASSWORD=${PYPI_PASSWORD} --rm -v `pwd`:/io $DOCKER_IMAGE /bin/bash
        ls
        ls wheelhouse/
        pip install twine
        twine upload ${TRAVIS_BUILD_DIR}/wheelhouse/pandas_plink*.whl \
            -u dhorta -p ${PYPI_PASSWORD}
    else
        ls dist
        pip install twine
        twine upload dist/pandas_plink*.whl -u dhorta -p ${PYPI_PASSWORD}
    fi
fi
