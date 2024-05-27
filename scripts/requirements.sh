#!/bin/bash

REQ_FILE="requirements.txt"

echo "install requirements"

# Check if requirements file is provided
if [ ! -z "$1" ]; then
  REQ_FILE=$1
fi

pip3 install -r $REQ_FILE