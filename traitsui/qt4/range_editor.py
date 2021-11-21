# (C) Copyright 2009-2021 Enthought, Inc., Austin, TX
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

""" Defines the various range editors and the range editor factory, for the
PyQt user interface toolkit.
"""


import ast
from math import log10

from pyface.qt import QtCore, QtGui

from traits.api import TraitError, Str, Float, Any, Bool

from .editor import Editor

from .constants import OKColor

from .helper import IconButton


# -------------------------------------------------------------------------
#  'BaseRangeEditor' class:
# -------------------------------------------------------------------------


class BaseRangeEditor(Editor):
    """The base class for Range editors. Using an evaluate trait, if specified,
    when assigning numbers the object trait.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Function to evaluate floats/ints
    evaluate = Any()

    def _set_value(self, value):
        if self.evaluate is not None:
            value = self.evaluate(value)
        Editor._set_value(self, value)

    #: Low value for the range
    low = Any()

    #: High value for the range
    high = Any()

    #: Deprecated: This trait is no longer used. See enthought/traitsui#1704
    format = Str()

    #: Flag indicating that the UI is in the process of being updated
    ui_changing = Bool(False)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._init_with_factory_defaults()
        self.control = self._make_control()
        self._do_layout(self.control)

    def _init_with_factory_defaults(self):
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, "evaluate", "from")

        self.sync_value(factory.low_name, "low", "from")
        self.sync_value(factory.high_name, "high", "from")

    def _make_control(self):
        raise NotImplementedError

    def _do_layout(self, control):
        raise NotImplementedError

    def _clip(self, fvalue, low, high):
        """Returns fvalue clipped between low and high"""

        try:
            if low is not None and fvalue < low:
                return low
            if high is not None and high < fvalue:
                return high
        except:
            return low
        return fvalue

    def _make_text_entry(self, fvalue_text):

        text = QtGui.QLineEdit(fvalue_text)
        # text.installEventFilter(text)
        if self.factory.enter_set:
            text.returnPressed.connect(self.update_object_on_enter)

        text.editingFinished.connect(self.update_object_on_enter)

        if self.factory.auto_set:
            text.textChanged.connect(self.update_object_on_enter)
        # The default size is a bit too big and probably doesn't need to grow.
        sh = text.sizeHint()
        sh.setWidth(sh.width() // 2)
        text.setMaximumSize(sh)
        self.set_tooltip(text)

        return text

    def _validate(self, value):
        if self.low is not None and value < self.low:
            message = "The value ({}) must be larger than {}!"
            raise ValueError(message.format(value, self.low))
        if self.high is not None and value > self.high:
            message = "The value ({}) must be smaller than {}!"
            raise ValueError(message.format(value, self.high))
        if not self.factory.is_float and isinstance(value, float):
            message = "The value must be an integer, but a value of {} was specified."
            raise ValueError(message.format(value))

    def _set_color(self, color):
        if self.control is not None:
            pal = QtGui.QPalette(self.control.text.palette())
            pal.setColor(QtGui.QPalette.Base, color)
            self.control.text.setPalette(pal)

    def update_object_on_enter(self):
        """Handles the user pressing the Enter key in the text field."""
        # It is possible the event is processed after the control is removed
        # from the editor
        if self.control is None:
            return

        try:
            value = ast.literal_eval(self.control.text.text())
            self._validate(value)
            self.value = value
        except Exception as excp:
            self.error(excp)
            return

        if not self.ui_changing:
            self._set_slider(value)

        self._set_color(OKColor)
        if self._error is not None:
            self._error = None
            self.ui.errors -= 1

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        if self._error is None:
            self._error = True
            self.ui.errors += 1
            super().error(excp)
        self.set_error_state(True)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        fvalue = self._clip(self.value, self.low, self.high)
        text = self.string_value(fvalue)

        self.ui_changing = True
        self.control.text.setText(text)
        self.ui_changing = False
        self._set_slider(fvalue)

    def _set_slider(self, value):
        """Updates the slider range controls."""
        # Do nothing for non-sliders.

    def _get_current_range(self):
        low, high = self.low, self.high
        return low, high

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self.control.text

    def _low_changed(self, low):
        if self.value < low:
            self.value = float(low) if self.factory.is_float else int(low)
        if self.control is not None:
            self.update_editor()

    def _high_changed(self, high):
        if self.value > high:
            self.value = float(high) if self.factory.is_float else int(high)
        if self.control is not None:
            self.update_editor()


class SimpleSliderEditor(BaseRangeEditor):
    """ Simple style of range editor that displays a slider and a text field.

    The user can set a value either by moving the slider or by typing a value
    in the text field.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:  See BaseRangeEditor
    # -------------------------------------------------------------------------

    def _make_control(self):

        low, high = self._get_current_range()
        fvalue = self._clip(self.value, low, high)
        fvalue_text = self.string_value(fvalue)

        width = self._get_default_width()

        control = QtGui.QWidget()
        control.label_lo = self._make_label_low(low, width)
        control.slider = self._make_slider(fvalue)
        control.label_hi = self._make_label_high(high, width)
        control.text = self._make_text_entry(fvalue_text)
        return control

    @staticmethod
    def _do_layout(control):
        layout = QtGui.QHBoxLayout(control)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(control.label_lo)
        layout.addWidget(control.slider)
        layout.addWidget(control.label_hi)
        layout.addWidget(control.text)

    def _get_default_width(self):
        return self.factory.label_width

    def _get_label_high(self, high):
        if self.factory.high_name != "":
            return self.string_value(high)
        return self.factory.high_label

    def _get_label_low(self, low):
        if self.factory.low_name != "":
            return self.string_value(low)
        return self.factory.low_label

    def _make_label_low(self, low, width):
        low_label = self._get_label_low(low)
        label_lo = QtGui.QLabel(low_label)
        label_lo.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        if width > 0:
            label_lo.setMinimumWidth(width)
        self.set_tooltip(label_lo)

        return label_lo

    def _make_slider(self, fvalue):
        ivalue = self._convert_to_slider(fvalue)
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setTracking(self.factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setValue(ivalue)
        slider.valueChanged.connect(self.update_object_on_scroll)
        self.set_tooltip(slider)

        return slider

    def _make_label_high(self, high, width):
        high_label = self._get_label_high(high)
        label_hi = QtGui.QLabel(high_label)
        if width > 0:
            label_hi.setMinimumWidth(width)
        self.set_tooltip(label_hi)

        return label_hi

    def update_object_on_scroll(self, pos):
        """Handles the user changing the current slider value."""
        value = self._convert_from_slider(pos)
        try:
            self.ui_changing = True
            self.control.text.setText(self.string_value(value))
            self.value = value
        except TraitError:
            pass
        finally:
            self.ui_changing = False

    def _set_slider(self, value):
        """Updates the slider range controls."""
        low, high = self._get_current_range()
        self.control.label_lo.setText(self.string_value(low))
        self.control.label_hi.setText(self.string_value(high))
        blocked = self.control.slider.blockSignals(True)
        try:
            ivalue = self._convert_to_slider(value)
            self.control.slider.setValue(ivalue)
        finally:
            self.control.slider.blockSignals(blocked)

    def _convert_to_slider(self, value):
        """Returns the slider setting corresponding to the user-supplied value."""
        low, high = self._get_current_range()
        if high > low:
            return int(float(value - low) / (high - low) * 10000.0)
        if low is None:
            return 0
        return low

    def _convert_from_slider(self, ivalue):
        """Returns the float or integer value corresponding to the slider
        setting.
        """
        low, high = self._get_current_range()
        value = low + ((float(ivalue) / 10000.0) * (high - low))
        if not self.factory.is_float:
            value = int(round(value))
        return value


# -------------------------------------------------------------------------
class LogRangeSliderEditor(SimpleSliderEditor):
    # -------------------------------------------------------------------------
    """A slider editor for log-spaced values"""

    def _convert_to_slider(self, value):
        """Returns the slider setting corresponding to the user-supplied value."""
        low, high = self._get_current_range()
        value = max(value, low)
        return int((log10(value) - log10(low)) / (log10(high) - log10(low)) * 10000.0)

    def _convert_from_slider(self, ivalue):
        """Returns the float or integer value corresponding to the slider
        setting.
        """
        low, high = self._get_current_range()
        value = float(ivalue) / 10000.0 * (log10(high) - log10(low))
        # Do this to handle floating point errors, where fvalue may exceed
        # self.high.
        fvalue = min(low * 10 ** (value), high)
        if not self.factory.is_float:
            fvalue = int(round(fvalue))
        return fvalue


class LargeRangeSliderEditor(SimpleSliderEditor):
    """A slider editor for large ranges.

    The editor displays a slider and a text field. A subset of the total
    range is displayed in the slider; arrow buttons at each end of the
    slider let the user move the displayed range higher or lower.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions: See BaseRangeEditor
    # -------------------------------------------------------------------------

    #: Low end of displayed slider range
    cur_low = Float()

    #: High end of displayed slider range
    cur_high = Float()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._init_with_factory_defaults()
        self.init_current_range(self.value)
        self.control = self._make_control(parent)
        # Set-up the layout:
        self._do_layout(self.control)

    def _make_control(self, parent):
        control = super()._make_control()
        low, high = self._get_current_range()

        control.button_lo = self._make_button_low(low)
        control.button_hi = self._make_button_high(high)
        return control

    @staticmethod
    def _do_layout(control):
        layout = QtGui.QHBoxLayout(control)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(control.label_lo)
        layout.addWidget(control.button_lo)
        layout.addWidget(control.slider)
        layout.addWidget(control.button_hi)
        layout.addWidget(control.label_hi)
        layout.addWidget(control.text)

    def _make_button_low(self, low):
        button_lo = IconButton(QtGui.QStyle.SP_ArrowLeft, self.reduce_range)
        button_lo.setEnabled(self.low is None or low != self.low)
        return button_lo

    def _make_button_high(self, high):
        button_hi = IconButton(QtGui.QStyle.SP_ArrowRight, self.increase_range)
        button_hi.setEnabled(self.high is None or high != self.high)
        return button_hi

    def _set_slider(self, value):
        """Updates the slider range controls."""
        low, high = self._get_current_range()
        if not low <= value <= high:
            low, high = self.init_current_range(value)
        ivalue = self._convert_to_slider(value)
        blocked = self.control.slider.blockSignals(True)
        try:
            self.control.slider.setValue(ivalue)
        finally:
            self.control.slider.blockSignals(blocked)

        fmt = self._get_format()
        self.control.label_lo.setText(fmt % low)
        self.control.label_hi.setText(fmt % high)

        self.control.button_lo.setEnabled(self.low is None or low != self.low)
        self.control.button_hi.setEnabled(self.high is None or high != self.high)

    def init_current_range(self, value):
        """Initializes the current slider range controls, cur_low and cur_high."""
        low, high = self.low, self.high

        mag = max(abs(value), 1)
        rounded_value = 10 ** int(log10(mag))
        fact_hi, fact_lo = (10, 1) if value >= 0 else (-1, -10)
        cur_low = rounded_value * fact_lo
        cur_high = rounded_value * fact_hi
        if mag <= 10:
            if value >= 0:
                cur_low *= -1
            else:
                cur_high *= -1

        if low is not None and cur_low < low:
            cur_low = low
        if high is not None and high < cur_high:
            cur_high = high

        self.cur_low, self.cur_high = cur_low, cur_high
        return self.cur_low, self.cur_high

    def reduce_range(self):
        """Reduces the extent of the displayed range."""
        value = self.value
        low = self.low

        old_cur_low = self.cur_low
        if abs(self.cur_low) < 10:
            value = value - 10
            self.cur_low = max(-10, low) if low is not None else -10
            if old_cur_low - self.cur_low > 9:
                self.cur_high = old_cur_low
        else:
            fact = 0.1 if self.cur_low > 0 else 10
            value = value * fact
            new_cur_low = self.cur_low * fact
            self.cur_low = max(low, new_cur_low) if low is not None else new_cur_low
            if self.cur_low == new_cur_low:
                self.cur_high = old_cur_low

        value = min(max(value, self.cur_low), self.cur_high)

        if self.factory.is_float is False:
            value = int(value)
        self.value = value
        self.update_editor()

    def increase_range(self):
        """Increased the extent of the displayed range."""
        value = self.value
        high = self.high
        old_cur_high = self.cur_high
        if abs(self.cur_high) < 10:
            value = value + 10
            self.cur_high = min(10, high) if high is not None else 10
            if self.cur_high - old_cur_high > 9:
                self.cur_low = old_cur_high
        else:
            fact = 10 if self.cur_high > 0 else 0.1
            value = value * fact
            new_cur_high = self.cur_high * fact
            self.cur_high = min(high, new_cur_high) if high is not None else new_cur_high
            if self.cur_high == new_cur_high:
                self.cur_low = old_cur_high

        value = min(max(value, self.cur_low), self.cur_high)

        if self.factory.is_float is False:
            value = int(value)

        self.value = value
        self.update_editor()

    def _get_format(self):
        if self.factory.is_float:
            low, high = self._get_current_range()
            diff = high - low
            if diff > 99999:
                return "%.2g"
            elif diff > 1:
                return "%%.%df" % max(0, 4 - int(log10(diff)))
            return "%.3f"
        return "%d"

    def _get_current_range(self):
        return self.cur_low, self.cur_high


class SimpleSpinEditor(BaseRangeEditor):
    """A simple style of range editor that displays a spin box control.

    The SimpleSpinEditor catches 3 different types of events that will increase/decrease
    the value of the class:
    1) Spin event generated by pushing the up/down spinbutton;
    2) Key pressed event generated by pressing the arrow- or page-up/down of the keyboard.
    3) Mouse wheel event generated by rolling the mouse wheel up or down.

    In addition, there are some other functionalities:

    - ``Shift`` + arrow = 2 * increment        (or ``Shift`` + mouse wheel);
    - ``Ctrl``  + arrow = 10 * increment       (or ``Ctrl`` + mouse wheel);
    - ``Alt``   + arrow = 100 * increment      (or ``Alt`` + mouse wheel);
    - Combinations of ``Shift``, ``Ctrl``, ``Alt`` increment the
      step value by the product of the factors;
    - ``PgUp`` & ``PgDn`` = 10 * increment * the product of the ``Shift``, ``Ctrl``, ``Alt``
      factors;
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:  See BaseRangeEditor
    # -------------------------------------------------------------------------

    #: Step value for the spinner
    step = Any(1)

    def _make_control(self):

        low, high = self._get_current_range()
        fvalue = self._clip(self.value, low, high)
        fvalue_text = self.string_value(fvalue)

        spin_up_or_down = self._spin

        class Control(QtGui.QWidget):
            def wheelEvent(self, event):
                delta = event.angleDelta()
                y = delta.y()
                x = delta.x()
                sign = 1 if x + y > 0 else -1
                spin_up_or_down(sign)

            def keyPressEvent(self, event):
                key = event.key()
                scale = 1 if key in {QtCore.Qt.Key_Up, QtCore.Qt.Key_Down} else 10
                if key in {QtCore.Qt.Key_Up, QtCore.Qt.Key_PageUp}:
                    spin_up_or_down(scale)
                elif key in {QtCore.Qt.Key_Down, QtCore.Qt.Key_PageDown}:
                    spin_up_or_down(-scale)

        control = Control()
        control.text = self._make_text_entry(fvalue_text)
        control.button_lo = self._make_button_low(fvalue)
        control.button_hi = self._make_button_high(fvalue)
        return control

    @staticmethod
    def _do_layout(control):
        height = control.text.minimumSizeHint().height()
        width = height // 2 - 1
        control.button_lo.setFixedSize(width, width)
        control.button_hi.setFixedSize(width, width)

        layout = QtGui.QHBoxLayout(control)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(control.text)
        vwidget = QtGui.QWidget()
        vlayout = QtGui.QVBoxLayout(vwidget)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.addWidget(control.button_hi)
        vlayout.addWidget(control.button_lo)
        layout.addWidget(vwidget)
        # layout.addStretch(1)
        # vwidget.resize(width, height)

    def _make_button_low(self, value):
        # icon = QtGui.QStyle.SP_ArrowDown
        icon = QtGui.QStyle.SP_TitleBarUnshadeButton
        button_lo = IconButton(icon, self.spin_down)
        button_lo.setEnabled(self.low is None or self.low < value)
        return button_lo

    def _make_button_high(self, value):
        #icon = QtGui.QStyle.SP_ArrowUp
        icon = QtGui.QStyle.SP_TitleBarShadeButton
        button_hi = IconButton(icon, self.spin_up)
        button_hi.setEnabled(self.high is None or value < self.high)
        return button_hi

    def _spin(self, sign):
        step = sign * self._get_modifier()
        value = self.value
        low, high = self._get_current_range()

        value = self._clip(value + step, low, high)

        if self.factory.is_float is False:
            value = int(value)
        self.value = value
        self.update_editor()

    def _get_modifier(self):
        QModifiers = QtGui.QApplication.keyboardModifiers()
        modifier = self.step
        if (QModifiers & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier:
            modifier = modifier * 2
        if (QModifiers & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier:
            modifier = modifier * 10
        if (QModifiers & QtCore.Qt.AltModifier) == QtCore.Qt.AltModifier:
            modifier = modifier * 100
        return modifier

    def spin_down(self):
        """Reduces the value."""
        self._spin(sign=-1)

    def spin_up(self):
        """Increases the value."""
        self._spin(sign=1)

    def _set_slider(self, value):
        """Updates the spinbutton controls."""
        low, high = self._get_current_range()
        self.control.button_lo.setEnabled(low is None or low < value)
        self.control.button_hi.setEnabled(high is None or value < high)


class RangeTextEditor(BaseRangeEditor):
    """Editor for ranges that displays a text field.

    If the user enters a value that is outside the allowed range,
    the background of the field changes color to indicate an error.
    """

    def _make_control(self):

        low, high = self._get_current_range()
        fvalue = self._clip(self.value, low, high)
        fvalue_text = self.string_value(fvalue)

        control = QtGui.QWidget()
        control.text = self._make_text_entry(fvalue_text)
        return control

    @staticmethod
    def _do_layout(control):
        layout = QtGui.QHBoxLayout(control)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(control.text)


# -------------------------------------------------------------------------
#  'SimpleEnumEditor' factory adaptor:
# -------------------------------------------------------------------------


def SimpleEnumEditor(parent, factory, ui, object, name, description, **kwargs):
    return CustomEnumEditor(
        parent, factory, ui, object, name, description, "simple"
    )


def CustomEnumEditor(
    parent, factory, ui, object, name, description, style="custom", **kwargs
):
    """Factory adapter that returns a enumeration editor of the specified
    style.
    """
    if factory._enum is None:
        import traitsui.editors.enum_editor as enum_editor

        factory._enum = enum_editor.ToolkitEditorFactory(
            values=list(range(factory.low, factory.high + 1)),
            cols=factory.cols,
        )

    if style == "simple":
        return factory._enum.simple_editor(
            ui, object, name, description, parent
        )

    return factory._enum.custom_editor(ui, object, name, description, parent)


# -------------------------------------------------------------------------
#  Defines the mapping between editor factory 'mode's and Editor classes:
# -------------------------------------------------------------------------

# Mapping between editor factory modes and simple editor classes
SimpleEditorMap = {
    "slider": SimpleSliderEditor,
    "xslider": LargeRangeSliderEditor,
    "spinner": SimpleSpinEditor,
    "enum": SimpleEnumEditor,
    "text": RangeTextEditor,
    "logslider": LogRangeSliderEditor,
}
# Mapping between editor factory modes and custom editor classes
CustomEditorMap = {
    "slider": SimpleSliderEditor,
    "xslider": LargeRangeSliderEditor,
    "spinner": SimpleSpinEditor,
    "enum": CustomEnumEditor,
    "text": RangeTextEditor,
    "logslider": LogRangeSliderEditor,
}
