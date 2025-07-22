#!/bin/bash

FIRST_ARG=$1

SCRIPT_PATH=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
PROJECT_PATH=$(dirname $SCRIPT_PATH)
VENV_DIR=.venv
VENV_PATH=$PROJECT_PATH/$VENV_DIR
PYTHON_VERSION=3.10
PYENV_VERSION=$(pyenv --version)

cd $PROJECT_PATH

# Install the python version with pyenv if pyenv is installed
# This must always be run in the project folder
if [[ "$PYENV_VERSION" =~ (pyenv )[0-9]\.[0-9]\.[0-9] ]]
then
  LATEST_PYTHON_VERSION=$(pyenv latest -k $PYTHON_VERSION)
  pyenv install -s $LATEST_PYTHON_VERSION
  pyenv local $LATEST_PYTHON_VERSION
fi

python3 -m venv $VENV_DIR

# Adding libraries
echo $PROJECT_PATH > $VENV_PATH/lib/python$PYTHON_VERSION/site-packages/api.pth

source $VENV_PATH/bin/activate

# Installing packages
pip3 install \
    black pydantic \
    ckanapi requests tqdm

if [ "$FIRST_ARG" == '--dev' ]
then
    pip3 install pytest
fi

