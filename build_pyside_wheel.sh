#!/bin/bash
set -e

if [ -f "${HOME}/.cache/PySide-1.2.4-cp34-cp34m-linux_x86_64.whl" ]; then
   echo "PySide wheel found"
else
   echo "Building PySide"

   git clone https://github.com/PySide/pyside-setup.git
   cd pyside-setup

   # now it is time to build the pyside wheels
   python setup.py bdist_wheel --qmake=/usr/bin/qmake-qt4 --version=1.2.4 --jobs=2
   ls dist/
   cp dist/PySide-1.2.4-cp34-cp34m-linux_x86_64.whl $HOME/.cache/
fi

pip install "${HOME}/.cache/PySide-1.2.4-cp34-cp34m-linux_x86_64.whl"
