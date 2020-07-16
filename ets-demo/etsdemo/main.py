# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" The main function for launching the demo application.
"""

from etsdemo.app import Demo, DemoEmpty


def _create_demo():
    """ Create the demo object with everything setup ready to be launched. """
    return Demo(model=DemoEmpty())


def main():
    """ Main function exposed to the entry point for launching the demo
    application.
    """
    demo = _create_demo()
    demo.configure_traits()
