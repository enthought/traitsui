#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various range editors and the range editor factory, for the
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from math \
    import log10

from pyface.qt import QtCore, QtGui

from traits.api \
    import TraitError, Str, Float, Any, Bool

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.range_editor file.
from traitsui.editors.range_editor \
    import ToolkitEditorFactory

from .editor_factory \
    import TextEditor

from .editor \
    import Editor

from .constants \
    import OKColor, ErrorColor

from .helper \
    import IconButton
import six

#-------------------------------------------------------------------------
#  'BaseRangeEditor' class:
#-------------------------------------------------------------------------


class BaseRangeEditor(Editor):
    """ The base class for Range editors. Using an evaluate trait, if specified,
        when assigning numbers the object trait.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Function to evaluate floats/ints
    evaluate = Any

    #-------------------------------------------------------------------------
    #  Sets the associated object trait's value:
    #-------------------------------------------------------------------------

    def _set_value(self, value):
        if self.evaluate is not None:
            value = self.evaluate(value)
        Editor._set_value(self, value)

#-------------------------------------------------------------------------
#  'SimpleSliderEditor' class:
#-------------------------------------------------------------------------


class SimpleSliderEditor(BaseRangeEditor):
    """ Simple style of range editor that displays a slider and a text field.

    The user can set a value either by moving the slider or by typing a value
    in the text field.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

    # Formatting string used to format value and labels
    format = Str

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.format = factory.format

        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        self.sync_value(factory.low_name, 'low', 'from')
        self.sync_value(factory.high_name, 'high', 'from')

        self.control = QtGui.QWidget()
        panel = QtGui.QHBoxLayout(self.control)
        panel.setContentsMargins(0, 0, 0, 0)

        fvalue = self.value

        try:
            if not (self.low <= fvalue <= self.high):
                fvalue = self.low
            fvalue_text = self.format % fvalue
        except:
            fvalue_text = ''
            fvalue = self.low

        ivalue = self._convert_to_slider(fvalue)

        self._label_lo = QtGui.QLabel()
        self._label_lo.setAlignment(QtCore.Qt.AlignRight |
                                    QtCore.Qt.AlignVCenter)
        if factory.label_width > 0:
            self._label_lo.setMinimumWidth(factory.label_width)
        panel.addWidget(self._label_lo)

        self.control.slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setTracking(factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setValue(ivalue)
        slider.valueChanged.connect(self.update_object_on_scroll)
        panel.addWidget(slider)

        self._label_hi = QtGui.QLabel()
        panel.addWidget(self._label_hi)
        if factory.label_width > 0:
            self._label_hi.setMinimumWidth(factory.label_width)

        self.control.text = text = QtGui.QLineEdit(fvalue_text)
        text.editingFinished.connect(self.update_object_on_enter)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = text.sizeHint()
        sh.setWidth(sh.width() / 2)
        text.setMaximumSize(sh)

        panel.addWidget(text)

        low_label = factory.low_label
        if factory.low_name != '':
            low_label = self.format % self.low

        high_label = factory.high_label
        if factory.high_name != '':
            high_label = self.format % self.high

        self._label_lo.setText(low_label)
        self._label_hi.setText(high_label)

        self.set_tooltip(slider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)
        self.set_tooltip(text)

    #-------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #-------------------------------------------------------------------------

    def update_object_on_scroll(self, pos):
        """ Handles the user changing the current slider value.
        """
        value = self._convert_from_slider(pos)
        self.control.text.setText(self.format % value)
        try:
            self.value = value
        except Exception as exc:
            from traitsui.api import raise_to_debug
            raise_to_debug()

    #-------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #-------------------------------------------------------------------------

    def update_object_on_enter(self):
        """ Handles the user pressing the Enter key in the text field.
        """
        # it is possible we get the event after the control has gone away
        if self.control is None:
            return

        try:
            try:
                value = eval(six.text_type(self.control.text.text()).strip())
            except Exception as ex:
                # The entered something that didn't eval as a number, (e.g.,
                # 'foo') pretend it didn't happen
                value = self.value
                self.control.text.setText(six.text_type(value))
                # for compound editor, value may be non-numeric
                if not isinstance(value, (int, float)):
                    return

            if not self.factory.is_float:
                value = int(value)

            self.value = value
            blocked = self.control.slider.blockSignals(True)
            try:
                self.control.slider.setValue(
                    self._convert_to_slider(self.value))
            finally:
                self.control.slider.blockSignals(blocked)
        except TraitError as excp:
            pass

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low = self.low
        high = self.high
        try:
            text = self.format % value
            1 / (low <= value <= high)
        except:
            text = ''
            value = low

        ivalue = self._convert_to_slider(value)

        self.control.text.setText(text)

        blocked = self.control.slider.blockSignals(True)
        try:
            self.control.slider.setValue(ivalue)
        finally:
            self.control.slider.blockSignals(blocked)

    #-------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #-------------------------------------------------------------------------

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self.control.text

    #-------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #-------------------------------------------------------------------------

    def _low_changed(self, low):
        if self.value < low:
            if self.factory.is_float:
                self.value = float(low)
            else:
                self.value = int(low)

        if self._label_lo is not None:
            self._label_lo.setText(self.format % low)
            self.update_editor()

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)

        if self._label_hi is not None:
            self._label_hi.setText(self.format % high)
            self.update_editor()

    def _convert_to_slider(self, value):
        """ Returns the slider setting corresponding to the user-supplied value.
        """
        if self.high > self.low:
            ivalue = int((float(value - self.low) /
                          (self.high - self.low)) * 10000.0)
        else:
            ivalue = self.low

            if ivalue is None:
                ivalue = 0
        return ivalue

    def _convert_from_slider(self, ivalue):
        """ Returns the float or integer value corresponding to the slider
        setting.
        """
        value = self.low + ((float(ivalue) / 10000.0) *
                            (self.high - self.low))
        if not self.factory.is_float:
            value = int(round(value))
        return value


#-------------------------------------------------------------------------
class LogRangeSliderEditor(SimpleSliderEditor):
    #-------------------------------------------------------------------------
    """ A slider editor for log-spaced values
    """

    def _convert_to_slider(self, value):
        """ Returns the slider setting corresponding to the user-supplied value.
        """
        value = max(value, self.low)
        ivalue = int((log10(value) - log10(self.low)) /
                     (log10(self.high) - log10(self.low)) * 10000.0)
        return ivalue

    def _convert_from_slider(self, ivalue):
        """ Returns the float or integer value corresponding to the slider
        setting.
        """
        value = float(ivalue) / 10000.0 * (log10(self.high) - log10(self.low))
        # Do this to handle floating point errors, where fvalue may exceed
        # self.high.
        fvalue = min(self.low * 10**(value), self.high)
        if not self.factory.is_float:
            fvalue = int(round(fvalue))
        return fvalue

#-------------------------------------------------------------------------
#  'LargeRangeSliderEditor' class:
#-------------------------------------------------------------------------


class LargeRangeSliderEditor(BaseRangeEditor):
    """ A slider editor for large ranges.

    The editor displays a slider and a text field. A subset of the total range
    is displayed in the slider; arrow buttons at each end of the slider let
    the user move the displayed range higher or lower.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Low value for the slider range
    low = Any(0)

    # High value for the slider range
    high = Any(1)

    # Low end of displayed range
    cur_low = Float

    # High end of displayed range
    cur_high = Float

    # Flag indicating that the UI is in the process of being updated
    ui_changing = Bool(False)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Initialize using the factory range defaults:
        self.low = factory.low
        self.high = factory.high
        self.evaluate = factory.evaluate

        # Hook up the traits to listen to the object.
        self.sync_value(factory.low_name, 'low', 'from')
        self.sync_value(factory.high_name, 'high', 'from')
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        self.init_range()
        low = self.cur_low
        high = self.cur_high

        self._set_format()

        self.control = QtGui.QWidget()
        panel = QtGui.QHBoxLayout(self.control)
        panel.setContentsMargins(0, 0, 0, 0)

        fvalue = self.value

        try:
            fvalue_text = self._format % fvalue
            1 / (low <= fvalue <= high)
        except:
            fvalue_text = ''
            fvalue = low

        if high > low:
            ivalue = int((float(fvalue - low) / (high - low)) * 10000)
        else:
            ivalue = low

        # Lower limit label:
        self.control.label_lo = label_lo = QtGui.QLabel()
        label_lo.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        panel.addWidget(label_lo)

        # Lower limit button:
        self.control.button_lo = IconButton(QtGui.QStyle.SP_ArrowLeft,
                                            self.reduce_range)
        panel.addWidget(self.control.button_lo)

        # Slider:
        self.control.slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setTracking(factory.auto_set)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setPageStep(1000)
        slider.setSingleStep(100)
        slider.setValue(ivalue)
        slider.valueChanged.connect(self.update_object_on_scroll)
        panel.addWidget(slider)

        # Upper limit button:
        self.control.button_hi = IconButton(QtGui.QStyle.SP_ArrowRight,
                                            self.increase_range)
        panel.addWidget(self.control.button_hi)

        # Upper limit label:
        self.control.label_hi = label_hi = QtGui.QLabel()
        panel.addWidget(label_hi)

        # Text entry:
        self.control.text = text = QtGui.QLineEdit(fvalue_text)
        text.editingFinished.connect(self.update_object_on_enter)

        # The default size is a bit too big and probably doesn't need to grow.
        sh = text.sizeHint()
        sh.setWidth(sh.width() / 2)
        text.setMaximumSize(sh)

        panel.addWidget(text)

        label_lo.setText(str(low))
        label_hi.setText(str(high))
        self.set_tooltip(slider)
        self.set_tooltip(label_lo)
        self.set_tooltip(label_hi)
        self.set_tooltip(text)

        # Update the ranges and button just in case.
        self.update_range_ui()

    #-------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #-------------------------------------------------------------------------

    def update_object_on_scroll(self, pos):
        """ Handles the user changing the current slider value.
        """
        value = self.cur_low + ((float(pos) / 10000.0)
                                * (self.cur_high - self.cur_low))

        self.control.text.setText(self._format % value)

        if self.factory.is_float:
            self.value = value
        else:
            self.value = int(value)

    #-------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #-------------------------------------------------------------------------

    def update_object_on_enter(self):
        """ Handles the user pressing the Enter key in the text field.
        """
        try:
            self.value = eval(six.text_type(self.control.text.text()).strip())
        except TraitError as excp:
            pass

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low = self.low
        high = self.high
        try:
            text = self._format % value
            1 / (low <= value <= high)
        except:
            value = low
        self.value = value

        if not self.ui_changing:
            self.init_range()
            self.update_range_ui()

    def update_range_ui(self):
        """ Updates the slider range controls.
        """
        low, high = self.cur_low, self.cur_high
        value = self.value
        self._set_format()
        self.control.label_lo.setText(self._format % low)
        self.control.label_hi.setText(self._format % high)

        if high > low:
            ivalue = int((float(value - low) / (high - low)) * 10000.0)
        else:
            ivalue = low

        blocked = self.control.slider.blockSignals(True)
        self.control.slider.setValue(ivalue)
        self.control.slider.blockSignals(blocked)

        text = self._format % self.value
        self.control.text.setText(text)
        self.control.button_lo.setEnabled(low != self.low)
        self.control.button_hi.setEnabled(high != self.high)

    def init_range(self):
        """ Initializes the slider range controls.
        """
        value = self.value
        low, high = self.low, self.high
        if (high is None) and (low is not None):
            high = -low

        mag = abs(value)
        if mag <= 10.0:
            cur_low = max(value - 10, low)
            cur_high = min(value + 10, high)
        else:
            d = 0.5 * (10**int(log10(mag) + 1))
            cur_low = max(low, value - d)
            cur_high = min(high, value + d)

        self.cur_low, self.cur_high = cur_low, cur_high

    def reduce_range(self):
        """ Reduces the extent of the displayed range.
        """
        low, high = self.low, self.high
        if abs(self.cur_low) < 10:
            self.cur_low = max(-10, low)
            self.cur_high = min(10, high)
        elif self.cur_low > 0:
            self.cur_high = self.cur_low
            self.cur_low = max(low, self.cur_low / 10)
        else:
            self.cur_high = self.cur_low
            self.cur_low = max(low, self.cur_low * 10)

        self.ui_changing = True
        self.value = min(max(self.value, self.cur_low), self.cur_high)
        self.ui_changing = False
        self.update_range_ui()

    def increase_range(self):
        """ Increased the extent of the displayed range.
        """
        low, high = self.low, self.high
        if abs(self.cur_high) < 10:
            self.cur_low = max(-10, low)
            self.cur_high = min(10, high)
        elif self.cur_high > 0:
            self.cur_low = self.cur_high
            self.cur_high = min(high, self.cur_high * 10)
        else:
            self.cur_low = self.cur_high
            self.cur_high = min(high, self.cur_high / 10)

        self.ui_changing = True
        self.value = min(max(self.value, self.cur_low), self.cur_high)
        self.ui_changing = False
        self.update_range_ui()

    def _set_format(self):
        self._format = '%d'
        factory = self.factory
        low, high = self.cur_low, self.cur_high
        diff = high - low
        if factory.is_float:
            if diff > 99999:
                self._format = '%.2g'
            elif diff > 1:
                self._format = '%%.%df' % max(0, 4 -
                                              int(log10(high - low)))
            else:
                self._format = '%.3f'

    #-------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #-------------------------------------------------------------------------

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self.control.text

    #-------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #-------------------------------------------------------------------------

    def _low_changed(self, low):
        if self.control is not None:
            if self.value < low:
                if self.factory.is_float:
                    self.value = float(low)
                else:
                    self.value = int(low)

            self.update_editor()

    def _high_changed(self, high):
        if self.control is not None:
            if self.value > high:
                if self.factory.is_float:
                    self.value = float(high)
                else:
                    self.value = int(high)

            self.update_editor()

#-------------------------------------------------------------------------
#  'SimpleSpinEditor' class:
#-------------------------------------------------------------------------


class SimpleSpinEditor(BaseRangeEditor):
    """ A simple style of range editor that displays a spin box control.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.sync_value(factory.low_name, 'low', 'from')
        self.sync_value(factory.high_name, 'high', 'from')
        low = self.low
        high = self.high

        self.control = QtGui.QSpinBox()
        self.control.setMinimum(low)
        self.control.setMaximum(high)
        self.control.setValue(self.value)
        self.control.valueChanged.connect(self.update_object)
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Handle the user selecting a new value from the spin control:
    #-------------------------------------------------------------------------

    def update_object(self, value):
        """ Handles the user selecting a new value in the spin box.
        """
        self._locked = True
        try:
            self.value = value
        finally:
            self._locked = False

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self._locked:
            blocked = self.control.blockSignals(True)
            try:
                self.control.setValue(int(self.value))
            except Exception:
                from traitsui.api import raise_to_debug
                raise_to_debug()
            finally:
                self.control.blockSignals(blocked)

    #-------------------------------------------------------------------------
    #  Handles the 'low'/'high' traits being changed:
    #-------------------------------------------------------------------------

    def _low_changed(self, low):
        if self.value < low:
            if self.factory.is_float:
                self.value = float(low)
            else:
                self.value = int(low)

        if self.control:
            self.control.setMinimum(low)
            self.control.setValue(int(self.value))

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)

        if self.control:
            self.control.setMaximum(high)
            self.control.setValue(int(self.value))

#-------------------------------------------------------------------------
#  'RangeTextEditor' class:
#-------------------------------------------------------------------------


class RangeTextEditor(TextEditor):
    """ Editor for ranges that displays a text field. If the user enters a
    value that is outside the allowed range, the background of the field
    changes color to indicate an error.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Function to evaluate floats/ints
    evaluate = Any

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        TextEditor.init(self, parent)
        self.evaluate = self.factory.evaluate
        self.sync_value(self.factory.evaluate_name, 'evaluate', 'from')

    #-------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #-------------------------------------------------------------------------

    def update_object(self):
        """ Handles the user entering input data in the edit control.
        """
        try:
            value = eval(six.text_type(self.control.text()))
            if self.evaluate is not None:
                value = self.evaluate(value)
            self.value = value
            col = OKColor
        except Exception:
            col = ErrorColor

        if self.control is not None:
            pal = QtGui.QPalette(self.control.palette())
            pal.setColor(QtGui.QPalette.Base, col)
            self.control.setPalette(pal)

#-------------------------------------------------------------------------
#  'SimpleEnumEditor' factory adaptor:
#-------------------------------------------------------------------------


def SimpleEnumEditor(parent, factory, ui, object, name, description):
    return CustomEnumEditor(parent, factory, ui, object, name, description,
                            'simple')

#-------------------------------------------------------------------------
#  'CustomEnumEditor' factory adaptor:
#-------------------------------------------------------------------------


def CustomEnumEditor(parent, factory, ui, object, name, description,
                     style='custom'):
    """ Factory adapter that returns a enumeration editor of the specified
    style.
    """
    if factory._enum is None:
        import traitsui.editors.enum_editor as enum_editor
        factory._enum = enum_editor.ToolkitEditorFactory(
            values=list(range(factory.low, factory.high + 1)),
            cols=factory.cols)

    if style == 'simple':
        return factory._enum.simple_editor(ui, object, name, description,
                                           parent)

    return factory._enum.custom_editor(ui, object, name, description, parent)

#-------------------------------------------------------------------------
#  Defines the mapping between editor factory 'mode's and Editor classes:
#-------------------------------------------------------------------------

# Mapping between editor factory modes and simple editor classes
SimpleEditorMap = {
    'slider': SimpleSliderEditor,
    'xslider': LargeRangeSliderEditor,
    'spinner': SimpleSpinEditor,
    'enum': SimpleEnumEditor,
    'text': RangeTextEditor,
    'logslider': LogRangeSliderEditor
}
# Mapping between editor factory modes and custom editor classes
CustomEditorMap = {
    'slider': SimpleSliderEditor,
    'xslider': LargeRangeSliderEditor,
    'spinner': SimpleSpinEditor,
    'enum': CustomEnumEditor,
    'text': RangeTextEditor,
    'logslider': LogRangeSliderEditor
}
