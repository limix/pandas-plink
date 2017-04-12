#!/usr/bin/env bash
set -e -x

if ! [ -z ${DOCKER_IMAGE+x} ]; then
    docker pull $DOCKER_IMAGE
fi
