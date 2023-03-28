# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the various color editors for the PyQt user interface toolkit.
"""


from pyface.qt import QtCore, QtGui, is_pyside

from traitsui.editors.color_editor import (
    ToolkitEditorFactory as BaseToolkitEditorFactory,
)

from .editor_factory import (
    SimpleEditor as BaseSimpleEditor,
    TextEditor as BaseTextEditor,
    ReadonlyEditor as BaseReadonlyEditor,
)

from .editor import Editor


# Standard color samples:
color_samples = []

# ---------------------------------------------------------------------------
#  The PyQt ToolkitEditorFactory class.
# ---------------------------------------------------------------------------

## We need to add qt-specific methods to the editor factory (since all editors
## will be accessing these functions. Making these functions global functions
## in this file does not work quite well, since we want custom editors to
## override these methods easily.


class ToolkitEditorFactory(BaseToolkitEditorFactory):
    """PyQt editor factory for color editors."""

    def to_qt_color(self, editor):
        """Gets the PyQt color equivalent of the object trait."""
        if self.mapped:
            return getattr(editor.object, editor.name + "_")

        return getattr(editor.object, editor.name)

    def from_qt_color(self, color):
        """Gets the application equivalent of a PyQt value."""
        return color

    def str_color(self, color):
        """Returns the text representation of a specified color value."""
        if isinstance(color, QtGui.QColor):
            alpha = color.alpha()
            if alpha == 255:
                return "(%d,%d,%d)" % (
                    color.red(),
                    color.green(),
                    color.blue(),
                )

            return "(%d,%d,%d,%d)" % (
                color.red(),
                color.green(),
                color.blue(),
                alpha,
            )

        return color


class SimpleColorEditor(BaseSimpleEditor):
    """Simple style of color editor, which displays a text field whose
    background color is the color value. Selecting the text field displays
    a dialog box for selecting a new color value.
    """

    def popup_editor(self):
        """Invokes the pop-up editor for an object trait."""
        color = self.factory.to_qt_color(self)
        options = QtGui.QColorDialog.ColorDialogOption.ShowAlphaChannel
        if not self.factory.use_native_dialog:
            options |= QtGui.QColorDialog.ColorDialogOption.DontUseNativeDialog
        color = QtGui.QColorDialog.getColor(
            color, self.control, "Select Color", options
        )

        if color.isValid():
            self.value = self.factory.from_qt_color(color)
            self.update_editor()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        super().update_editor()
        set_color(self)

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        return self.factory.str_color(color)


class CustomColorEditor(Editor):
    """Custom style of color editor, which displays a color editor panel."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control, self._simple_field = color_editor_for(self, parent)

    def dispose(self):
        """Disposes of the contents of an editor."""
        if getattr(self, "_simple_field", None) is not None:
            self._simple_field.dispose()
            self._simple_field = None
        super().dispose()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        self._simple_field.update_editor()

    def update_object_from_swatch(self, color_text):
        """Updates the object trait when a color swatch is clicked."""
        color = QtGui.QColor(*[int(part) for part in color_text.split(",")])
        self.value = self.factory.from_qt_color(color)
        self.update_editor()

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        return self.factory.str_color(color)


class TextColorEditor(BaseTextEditor):
    """Text style of color editor, which displays a text field whose
    background color is the color value.
    """

    def update_object(self):
        """Handles the user changing the contents of the edit control."""
        self.value = str(self.control.text())
        set_color(self)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        super().update_editor()
        set_color(self)

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        return self.factory.str_color(color)


class ReadonlyColorEditor(BaseReadonlyEditor):
    """Read-only style of color editor, which displays a read-only text field
    whose background color is the color value.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QLineEdit()
        self.control.setReadOnly(True)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        super().update_editor()
        set_color(self)

    def string_value(self, color):
        """Returns the text representation of a specified color value."""
        return self.factory.str_color(color)


# -------------------------------------------------------------------------
#   Sets the color of the specified editor's color control:
# -------------------------------------------------------------------------


def set_color(editor):
    """Sets the color of the specified color control."""
    color = editor.factory.to_qt_color(editor)
    pal = QtGui.QPalette(editor.control.palette())

    pal.setColor(QtGui.QPalette.ColorRole.Base, color)

    if color.red() > 192 or color.blue() > 192 or color.green() > 192:
        pal.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.black)
    else:
        pal.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)

    editor.control.setPalette(pal)


# ----------------------------------------------------------------------------
#  Creates a custom color editor panel for a specified editor:
# ----------------------------------------------------------------------------


class FixedButton(QtGui.QPushButton):
    """Override to work around a bug in Qt 4.7 on Macs.

    https://bugreports.qt-project.org/browse/QTBUG-15936
    """

    def hitButton(self, pos):
        return QtGui.QAbstractButton.hitButton(self, pos)


def color_editor_for(editor, parent):
    """Creates a custom color editor panel for a specified editor."""
    # Create the colour samples if it hasn't already been done.
    if len(color_samples) == 0:
        color_choices = (0, 128, 192, 255)
        for r in color_choices:
            for g in color_choices:
                for b in (0, 128, 255):
                    color_samples.append(QtGui.QColor(r, g, b))

    root = QtGui.QWidget()
    panel = QtGui.QHBoxLayout(root)
    panel.setContentsMargins(0, 0, 0, 0)

    swatch_editor = editor.factory.simple_editor(
        editor.ui, editor.object, editor.name, editor.description, None
    )
    swatch_editor.prepare(parent)
    panel.addWidget(swatch_editor.control)

    # Add all of the color choice buttons:
    grid = QtGui.QGridLayout()
    grid.setSpacing(0)

    mapper = QtCore.QSignalMapper(panel)

    rows = 4
    cols = len(color_samples) // rows
    i = 0

    sheet_template = """
    QPushButton {
        min-height: 18px;
        max-height: 18px;
        min-width: 18px;
        max-width: 18px;
        background-color: rgb(%s);
    }
    """

    for r in range(rows):
        for c in range(cols):
            control = FixedButton()
            color = color_samples[r * cols + c]
            color_text = "%d,%d,%d,%d" % color.getRgb()
            control.setStyleSheet(sheet_template % color_text)
            control.setAttribute(QtCore.Qt.WidgetAttribute.WA_LayoutUsesWidgetRect, True)

            control.clicked.connect(mapper.map)
            mapper.setMapping(control, color_text)

            grid.addWidget(control, r, c)
            editor.set_tooltip(control)

            i += 1

    if is_pyside and QtCore.__version_info__ >= (5, 15):
        mapper.mappedString.connect(editor.update_object_from_swatch)
    else:
        mapper.mapped[str].connect(editor.update_object_from_swatch)

    panel.addLayout(grid)

    return root, swatch_editor


# Define the SimpleEditor, CustomEditor, etc. classes which are used by the
# editor factory for the color editor.
SimpleEditor = SimpleColorEditor
CustomEditor = CustomColorEditor
TextEditor = TextColorEditor
ReadonlyEditor = ReadonlyColorEditor
