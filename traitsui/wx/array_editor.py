# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines array editors for the WX user interface toolkit.
"""


from traitsui.editors.array_editor import SimpleEditor as BaseSimpleEditor

from .editor import Editor

# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(BaseSimpleEditor, Editor):
    """Simple style of editor for arrays."""

    # FIXME: This class has been re-defined here simply so it inherits from the
    # wx Editor class.
    pass


class ReadonlyEditor(SimpleEditor):

    #: Set the value of the readonly trait.
    readonly = True
