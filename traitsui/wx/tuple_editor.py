# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the tuple editor for the wxPython user interface toolkit.
"""


from traitsui.editors.tuple_editor import SimpleEditor as BaseSimpleEditor

from .editor import Editor

# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(BaseSimpleEditor, Editor):
    """Simple style of editor for tuples.

    The editor displays an editor for each of the fields in the tuple,
    based on the type of each field.
    """

    pass
