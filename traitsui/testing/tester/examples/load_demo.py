#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#


def load_demo(file_path, variable_name="demo"):
    """ Loads a demo example from given file_path. Extracts the relevant
    object via variable_name.

    Parameters
    ----------
    file_path : str
        The file_path of the file to be loaded
    variable_name : str
        The key in the global symbol state corresponding to the object of
        interest for the demo.
    
    Returns
    -------
    Instance of HasTraits
        It is expected that this object will have edit_traits called on it,
        so that the demo can be tested.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    globals_ = globals().copy()
    exec(content, globals_)
    return globals_[variable_name]