#!/bin/bash

set -e -x

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    source ~/.venv/bin/activate
    brew install pandoc libffi
fi

pip install pypandoc
python -c "from pypandoc import download_pandoc as dp; dp(targetfolder='~/bin/');"
