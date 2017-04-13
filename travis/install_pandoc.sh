#!/bin/bash

set -e -x

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    brew install python3 pandoc libffi
    wget https://bootstrap.pypa.io/get-pip.py
    sudo python get-pip.py
fi

sudo pip install pypandoc
sudo python -c "from pypandoc import download_pandoc as dp; dp(targetfolder='~/bin/');"
