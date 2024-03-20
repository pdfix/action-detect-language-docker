#!/bin/bash

activate_venv_unix() {
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "env" ]; then
        source env/bin/activate
    else
        read -p "Python virtual environment 'venv' or 'env' not found. Do you want to create it automatically? (y/n): " create_venv
        if [ "$create_venv" == "y" ] || [ "$create_venv" == "Y" ]; then
            echo "Creating Python virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
        else
            echo "Exiting program. Please create the virtual environment 'venv' manually."
            exit 1
        fi
    fi
}

activate_venv_win() {
    if [ -d "venv" ]; then
        source venv/Scripts/activate
    elif [ -d "env" ]; then
        source env/Scrits/activate
    else
        read -p "Python virtual environment 'venv' or 'env' not found. Do you want to create it automatically? (y/n): " create_venv
        if [ "$create_venv" == "y" ] || [ "$create_venv" == "Y" ]; then
            echo "Creating Python virtual environment..."
            python -m venv venv
            source venv/Scripts/activate
        else
            echo "Exiting program. Please create the virtual environment 'venv' manually."
            exit 1
        fi
    fi
}

install_dependencies() {
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found. No dependencies installed."
    fi
}

if [[ "$(uname -s)" = "Linux" ]] || [[ "$(uname -s)" = "Darwin" ]]; then
	activate_venv_unix
elif [[ "$(uname -o)" = "Msys" ]]; then
	activate_venv_win
else
	echo "Unsupported OS type: $(uname -s)"
    exit 1
fi

run_pyinstaller() {
    local spec_file="$1"
    pyinstaller "$spec_file"
}

install_dependencies

echo 'Building executable...'
run_pyinstaller "lang_detect.spec"
