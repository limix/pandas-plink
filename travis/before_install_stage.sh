#!/usr/bin/env bash
set -e -x

if [ -z ${DOCKER_IMAGE+x} ]; then

    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        brew update || brew update
        git clone --depth 1 https://github.com/yyuu/pyenv.git ~/.pyenv

        PYENV_ROOT="$HOME/.pyenv"
        PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"

        case "${PYENV}" in
            py27)
                curl -O https://bootstrap.pypa.io/get-pip.py
                python get-pip.py --user
                ;;
            py35)
                pyenv install 3.5.2
                pyenv global 3.5.2
                ;;
            py36)
                pyenv install 3.6.0
                pyenv global 3.6.0
                ;;
        esac
        pyenv rehash
        python -m pip install --user virtualenv

        python -m virtualenv ~/.venv
        source ~/.venv/bin/activate
    fi
    travis/install_pandoc.sh
fi
