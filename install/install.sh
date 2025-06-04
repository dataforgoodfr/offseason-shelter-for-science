#!/bin/bash

SCRIPT_PATH=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
PROJECT_PATH=$(dirname $SCRIPT_PATH)
VENV_DIR=.venv
VENV_PATH=$PROJECT_PATH/$VENV_DIR
PYTHON_VERSION=3.10

cd $PROJECT_PATH

python3 -m venv $VENV_DIR

# Adding libraries
echo $PROJECT_PATH > $VENV_PATH/lib/python$PYTHON_VERSION/site-packages/api.pth

source $VENV_PATH/bin/activate

# Installing packages
pip3 install requests ckanapi tqdm pydantic
