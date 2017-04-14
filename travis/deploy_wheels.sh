#!/bin/bash

set -e -x

if ! [ -z ${DOCKER_IMAGE+x} ]; then
    docker run -e PYPI_PASSWORD=${PYPI_PASSWORD} --rm -v `pwd`:/io $DOCKER_IMAGE /bin/bash
    ls
    ls wheelhouse/
    pip install twine
    twine upload ${TRAVIS_BUILD_DIR}/wheelhouse/pandas_plink*.whl \
          -u dhorta -p ${PYPI_PASSWORD}
else
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        ls dist
        source ~/.venv/bin/activate
        pip install twine
        twine upload ${TRAVIS_BUILD_DIR}/dist/pandas_plink*.whl \
              -u dhorta -p ${PYPI_PASSWORD}
    fi
fi
