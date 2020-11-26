# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import pkg_resources

from etsdemo.version import version

ICON = pkg_resources.resource_filename("etsdemo", "images/enthought-icon.png")


def info():
    """ Provides information to the "eam" package. """
    return {
        "name": "ETS Demo",
        "description": "Application for browsing ETS examples and demos",
        "license": "BSD",
        "copyright": "(c) 2020 Enthought",
        "version": version,
        "schema_version": 2,
        "commands": [
            {
                "name": "ETS Demo",
                "command": "etsdemo",
                "icon": ICON,
            },
        ],
    }
