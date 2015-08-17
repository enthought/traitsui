#!/bin/bash
set -e

if [ -f "${HOME}/.cache/PySide-1.2.2-cp32-cp32mu-linux_x86_64.whl" ]; then
   echo "PySide wheel found"
else
   echo "Building PySide"

   git clone git@github.com:PySide/pyside-setup
   cd pyside-setup

   # The normal pyside repos only have the right tags upto 1.1.1
   # So we need to replace the repos with the newer ones
   git submodule deinit .
   git rm sources/pyside
   git rm sources/shiboken
   git submodule add --name sources/shiboken -- git@github.com:PySide/shiboken2 sources/shiboken
   git submodule add --name sources/pyside -- git@github.com:PySide/pyside2 sources/pyside
   git submodule sync

   # now it is time to build the pyside wheels
   python setup.py bdist_wheel --qmake=/usr/bin/qmake-qt4 --version=1.2.2

fi

pip install "${HOME}/.cache/wxPython-2.8.12.1-cp27-none-linux_x86_64.whl"
