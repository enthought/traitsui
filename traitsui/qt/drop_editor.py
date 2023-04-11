# (C) Copyright 2009-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines a drop target editor for the PyQt user interface toolkit. A drop
target editor handles drag and drop operations as a drop target.
"""


from pyface.qt import QtGui, QtCore

from .editor import Editor as _BaseEditor
from .text_editor import SimpleEditor as Editor
from .constants import DropColor
from .clipboard import PyMimeData, clipboard


class SimpleEditor(Editor):
    """Simple style of drop editor, which displays a read-only text field that
    contains the string representation of the object trait's value.
    """

    #: Background color when it is OK to drop objects.
    ok_color = DropColor

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        if self.factory.readonly:
            self.control = QtGui.QLineEdit(self.str_value)
            self.control.setReadOnly(True)
            self.set_tooltip()
        else:
            super().init(parent)

        pal = QtGui.QPalette(self.control.palette())
        pal.setColor(QtGui.QPalette.ColorRole.Base, self.ok_color)
        self.control.setPalette(pal)

        # Install EventFilter on control to handle DND events.
        drop_event_filter = _DropEventFilter(self.control)
        self.control.installEventFilter(drop_event_filter)

        self.control._qt_editor = self

    def dispose(self):
        """Disposes of the content of an editor."""
        if self.factory.readonly:
            # enthought/traitsui#884
            _BaseEditor.dispose(self)
        else:
            super().dispose()

    def string_value(self, value):
        """Returns the text representation of a specified object trait value."""
        if value is None:
            return ""
        return str(value)

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        pass


class _DropEventFilter(QtCore.QObject):
    def eventFilter(self, source, event):
        typ = event.type()
        if typ == QtCore.QEvent.Type.Drop:
            self.dropEvent(event)
        elif typ == QtCore.QEvent.Type.DragEnter:
            self.dragEnterEvent(event)
        return super().eventFilter(source, event)

    def dropEvent(self, e):
        """Handles a Python object being dropped on the tree."""
        editor = self.parent()._qt_editor

        klass = editor.factory.klass

        if editor.factory.binding:
            value = getattr(clipboard, "node", None)
        else:
            value = e.mimeData().instance()

        if (klass is None) or isinstance(value, klass):
            editor._no_update = True
            try:
                if hasattr(value, "drop_editor_value"):
                    editor.value = value.drop_editor_value()
                else:
                    editor.value = value
                if hasattr(value, "drop_editor_update"):
                    value.drop_editor_update(self)
                else:
                    self.setText(editor.str_value)
            finally:
                editor._no_update = False

            e.acceptProposedAction()

    def dragEnterEvent(self, e):
        """Handles a Python object being dragged over the tree."""
        editor = self.parent()._qt_editor

        if editor.factory.binding:
            data = getattr(clipboard, "node", None)
        else:
            md = e.mimeData()

            if not isinstance(md, PyMimeData):
                return

            data = md.instance()

        try:
            editor.object.base_trait(editor.name).validate(
                editor.object, editor.name, data
            )
            e.acceptProposedAction()
        except:
            pass


# Define the Text and ReadonlyEditor for use by the editor factory.
TextEditor = ReadonlyEditor = SimpleEditor
