""" Defines the various range editors and the range editor factory, for the
ipywidgets user interface toolkit.
"""

from math import log10

import ipywidgets as widgets

from traits.api import Str, Float, Any, Bool

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.range_editor file.
from traitsui.editors.range_editor import ToolkitEditorFactory

from .text_editor import SimpleEditor as TextEditor

from .editor import Editor


class BaseRangeEditor(Editor):
    """ The base class for Range editors. Using an evaluate trait, if specified,
        when assigning numbers the object trait.
    """

    #  **Traits**

    # Function to evaluate floats/ints
    evaluate = Any

    def _set_value(self, value):
        """Sets the associated object trait's value"""
        if self.evaluate is not None:
            value = self.evaluate(value)
        Editor._set_value(self, value)


class SimpleSliderEditor(BaseRangeEditor):
    """ Simple style of range editor that displays a slider and a text field.

    The user can set a value either by moving the slider or by typing a value
    in the text field.
    """

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

    # Formatting string used to format value and labels
    format = Str

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

        if self.factory.is_float:
            self.control = widgets.FloatSlider()
            step = (self.high - self.low)/1000
        else:
            self.control = widgets.IntSlider()
            step = 1

        fvalue = self.value

        try:
            if not (self.low <= fvalue <= self.high):
                fvalue = self.low
        except:
            fvalue = self.low

        slider = self.control
        slider.min = self.low
        slider.max = self.high
        slider.step = step
        slider.value = fvalue
        slider.readout = True
        if not self.factory.is_float:
            slider.readout_format = 'd'
        elif self.format:
            slider.readout_format = self.format[1:]

        slider.observe(self.update_object_on_scroll, 'value')

        self.set_tooltip(slider)

    def update_object_on_scroll(self, event=None):
        """ Handles the user changing the current slider value.
        """
        try:
            self.value = self.control.value
        except Exception as exc:
            from traitsui.api import raise_to_debug
            raise_to_debug()

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low = self.low
        high = self.high
        self.control.min = low
        self.control.max = high
        value = min(max(value, low), high)
        self.control.value = value

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self.control

    def _low_changed(self, low):
        if self.value < low:
            if self.factory.is_float:
                self.value = float(low)
            else:
                self.value = int(low)

        if self.control is not None:
            self.control.min = low

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)

        if self.control is not None:
            self.control.max = high


class LogRangeSliderEditor(SimpleSliderEditor):

    """ A slider editor for log-spaced values
    """
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

        self.control = widgets.FloatLogSlider()
        fvalue = self.value

        try:
            if not (self.low <= fvalue <= self.high):
                fvalue = self.low
        except:
            fvalue = self.low

        slider = self.control
        slider.base = 10
        mn, mx = log10(self.low), log10(self.high)
        slider.min = mn
        slider.max = mx
        slider.value = self.value
        slider.step = (mx - mn)/1000
        slider.observe(self.update_object_on_scroll, 'value')

        self.set_tooltip(slider)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low = log10(self.low)
        high = log10(self.high)
        self.control.min = low
        self.control.max = high
        value = min(max(value, self.low), self.high)
        self.control.value = value

    def _low_changed(self, low):
        if self.value < low:
            if self.factory.is_float:
                self.value = float(low)
            else:
                self.value = int(low)

        if self.control is not None:
            self.control.min = log10(low)

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)

        if self.control is not None:
            self.control.max = log10(high)


class LargeRangeSliderEditor(BaseRangeEditor):
    """ A slider editor for large ranges.

    The editor displays a slider and a text field. A subset of the total range
    is displayed in the slider; arrow buttons at each end of the slider let
    the user move the displayed range higher or lower.
    """

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

    left_control = Any
    right_control = Any
    slider = Any

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

        layout = widgets.Layout(width='40px')
        self.left_control = widgets.Button(icon='arrow-left', layout=layout)
        self.right_control = widgets.Button(icon='arrow-right', layout=layout)

        if self.factory.is_float:
            self.slider = widgets.FloatSlider()
            step = (self.high - self.low)/1000
        else:
            self.slider = widgets.IntSlider()
            step = 1

        self.control = widgets.HBox(
            [self.left_control, self.slider, self.right_control]
        )

        fvalue = self.value

        try:
            1 / (low <= fvalue <= high)
        except:
            fvalue = low

        slider = self.slider
        slider.min = 0
        slider.max = 10000
        slider.step = step
        slider.value = fvalue

        slider.readout = True
        if not self.factory.is_float:
            slider.readout_format = 'd'

        slider.observe(self.update_object_on_scroll, 'value')
        self.left_control.on_click(self.reduce_range)
        self.right_control.on_click(self.increase_range)

        # Text entry:
        self.set_tooltip(slider)
        self.set_tooltip(self.left_control)
        self.set_tooltip(self.right_control)

        # Update the ranges and button just in case.
        self.update_range_ui()

    def update_object_on_scroll(self, event=None):
        """ Handles the user changing the current slider value.
        """
        if not self.ui_changing:
            try:
                self.value = self.slider.value
            except Exception as exc:
                from traitsui.api import raise_to_debug
                raise_to_debug()

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        low = self.low
        high = self.high
        try:
            1 / (low <= value <= high)
        except:
            value = low

        if self.factory.is_float:
            self.value = float(value)
        else:
            self.value = int(value)

        self.init_range()
        self.ui_changing = True
        self.update_range_ui()
        self.slider.value = self.value
        self.ui_changing = False

    def update_range_ui(self):
        """ Updates the slider range controls.
        """
        low, high = self.cur_low, self.cur_high
        self.slider.min = low
        self.slider.max = high
        self.slider.step = (high - low)/1000

        self._set_format()

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

    def reduce_range(self, event=None):
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

        self.update_range_ui()
        self.value = min(max(self.value, self.cur_low), self.cur_high)

    def increase_range(self, event=None):
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

        self.update_range_ui()
        self.value = min(max(self.value, self.cur_low), self.cur_high)

    def _set_format(self):
        self._format = '%d'
        factory = self.factory
        low, high = self.cur_low, self.cur_high
        diff = high - low
        if factory.is_float:
            if diff > 99999:
                self._format = '.2g'
            elif diff > 1:
                self._format = '.%df' % max(0, 4 -
                                            int(log10(high - low)))
            else:
                self._format = '.3f'

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self.control

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


class SimpleSpinEditor(BaseRangeEditor):
    """ A simple style of range editor that displays a spin box control.
    """

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

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

        if self.factory.is_float:
            self.control = widgets.FloatText()
        else:
            self.control = widgets.IntText()
        self.control.value = self.value
        self.control.observe(self.update_object, 'value')
        self.set_tooltip()

    def update_object(self, event=None):
        """ Handles the user selecting a new value in the spin box.
        """
        val = self.control.value
        self.value = min(max(val, self.low), self.high)
        if self.value != val:
            self.control.value = self.value

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.value = self.value

    def _low_changed(self, low):
        if self.value < low:
            if self.factory.is_float:
                self.value = float(low)
            else:
                self.value = int(low)

        if self.control:
            self.control.value = self.value

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)

        if self.control:
            self.control.value = self.value


class RangeTextEditor(TextEditor):
    """ Editor for ranges that displays a text field. If the user enters a
    value that is outside the allowed range, the background of the field
    changes color to indicate an error.
    """

    # Function to evaluate floats/ints
    evaluate = Any

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        TextEditor.init(self, parent)
        self.evaluate = self.factory.evaluate
        self.sync_value(self.factory.evaluate_name, 'evaluate', 'from')

    def update_object(self):
        """ Handles the user entering input data in the edit control.
        """
        if (not self._no_update) and (self.control is not None):
            try:
                value = eval(self.control.value)
                if self.evaluate is not None:
                    value = self.evaluate(value)
                self.value = value
                self.set_error_state(False)
            except:
                self.set_error_state(True)


def SimpleEnumEditor(parent, factory, ui, object, name, description):
    return CustomEnumEditor(parent, factory, ui, object, name, description,
                            'simple')


def CustomEnumEditor(parent, factory, ui, object, name, description,
                     style='custom'):
    """ Factory adapter that returns a enumeration editor of the specified
    style.
    """
    if factory._enum is None:
        import traitsui.editors.enum_editor as enum_editor
        factory._enum = enum_editor.ToolkitEditorFactory(
            values=range(factory.low, factory.high + 1),
            cols=factory.cols)

    if style == 'simple':
        return factory._enum.simple_editor(ui, object, name, description,
                                           parent)

    return factory._enum.custom_editor(ui, object, name, description, parent)


# Defines the mapping between editor factory 'mode's and Editor classes:
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
