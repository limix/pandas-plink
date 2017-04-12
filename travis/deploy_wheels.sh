#!/usr/bin/env bash
set -e -x

if ! [ -z ${DOCKER_IMAGE+x} ]; then
  pip install twine
  twine upload ${TRAVIS_BUILD_DIR}/dist/*.whl \
        -u dhorta -p PYPI_PASSWORD
fi
