# -------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -------------------------------------------------------------------------

""" Script to run the tutorial.
"""


import os
import sys

from traitsui.extras.demo import demo

# Correct program usage information:
usage = """
Correct usage is: tutor.py [root_dir]
where:
    root_dir = Path to root of the tutorial tree

If omitted, 'root_dir' defaults to the current directory."""


def main(root_dir):
    # Create a tutor and display the tutorial:
    path, name = os.path.splitext(root_dir)
    demo(dir_name=root_dir)


if __name__ == '__main__':

    # Validate the command line arguments:
    if len(sys.argv) != 2:
        print(usage)
        sys.exit(1)

    root_dir = sys.argv[1]
    try:
        main(root_dir)
    except NameError as e:
        print(e)
        print(usage)
