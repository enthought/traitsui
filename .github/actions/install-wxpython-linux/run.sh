#!/bin/bash
# An environment variable VERSION_RANGE can be set to specific version
# range, in a format understood by pip.

set -e

install_wxpython_ubuntu() {
    local LINUX_NAME="$(lsb_release -i | cut -c 17-)"
    if [ "$LINUX_NAME" != "Ubuntu" ]; then
        echo "Unknown Linux Distribution"
        exit 1
    fi

    local UBUNTU_VERSION="$(lsb_release -r | cut -c 10-)"
    python -m pip install -f "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-$UBUNTU_VERSION/" "wxPython$VERSION_RANGE"
}

install_wxpython_ubuntu
