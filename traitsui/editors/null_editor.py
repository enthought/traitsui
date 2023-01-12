# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a completely empty editor, intended to be used as a spacer.
"""

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object

# Callable which returns the editor to use in the ui.


def null_editor(*args, **traits):
    return toolkit_object("null_editor:NullEditor")(*args, **traits)


# -------------------------------------------------------------------------
#  Create the editor factory object:
# -------------------------------------------------------------------------
NullEditor = BasicEditorFactory(klass=null_editor)
