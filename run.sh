#!/bin/bash
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Python is not installed. Please install it from:"
    echo "https://www.python.org/downloads/"
    exit 1
fi
pythonw zonepaq &
exit
