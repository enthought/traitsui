# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a text editor which displays a text field and maintains a history
    of previously entered values.
"""

from traits.api import Int, Bool

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object

# Define callable which returns the 'klass' value (i.e. the editor to use in
# the EditorFactory.


def history_editor(*args, **traits):
    return toolkit_object("history_editor:_HistoryEditor")(*args, **traits)


# -------------------------------------------------------------------------
#  Create the editor factory object:
# -------------------------------------------------------------------------


class ToolkitEditorFactory(BasicEditorFactory):

    #: The number of entries in the history:
    entries = Int(10)

    #: Should each keystroke update the value (or only the enter key, tab,
    #: etc.)?
    auto_set = Bool(False)


HistoryEditor = ToolkitEditorFactory(klass=history_editor)
