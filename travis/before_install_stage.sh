#!/usr/bin/env bash
set -e -x

if [ -z ${DOCKER_IMAGE+x} ]; then
    if [ "${NUMBA}" == "true" ]; then
        travis/install_clang38.sh;
        travis/install_llvmlite.sh;
    fi
    travis/install_pandoc.sh
fi
