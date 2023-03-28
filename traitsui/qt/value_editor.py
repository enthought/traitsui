# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the tree-based Python value editor and the value editor factory,
    for the wxPython user interface toolkit.
"""


from traitsui.editors.value_editor import _ValueEditor

from .editor import Editor


class SimpleEditor(_ValueEditor, Editor):
    """Returns the editor to use for simple style views."""

    #: Override the value of the readonly trait.
    readonly = False


class ReadonlyEditor(_ValueEditor, Editor):
    """Returns the editor to use for readonly style views."""

    #: Override the value of the readonly trait.
    readonly = True
