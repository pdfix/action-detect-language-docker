#!/bin/bash

# init
pushd "$(dirname $0)"

# activate Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
if [[ "$(uname -o)" = "Msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# build executable
echo 'Building executable...'
pyinstaller "lang_detect.spec"
