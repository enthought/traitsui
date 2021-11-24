# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various range editors for the wxPython user interface toolkit.
"""


import ast
from decimal import Decimal
from math import log10

import wx

from traits.api import TraitError, Str, Float, Any, Bool

from .editor import Editor

from .constants import OKColor

from .helper import TraitsUIPanel, Slider

# pylint: disable=no-member
if not hasattr(wx, "wx.wxEVT_SCROLL_ENDSCROLL"):
    wxEVT_SCROLL_ENDSCROLL = wx.wxEVT_SCROLL_CHANGED
else:
    wxEVT_SCROLL_ENDSCROLL = wx.wxEVT_SCROLL_ENDSCROLL  # @UndefinedVariable


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
        self.control = self._make_control(parent)
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

    def _make_control(self, parent):
        raise NotImplementedError

    def _do_layout(self, control):
        raise NotImplementedError

    def _clip(self, fvalue, low, high):
        """Returns fvalue clipped between low and high"""

        if low is not None and fvalue < low:
            return low
        if high is not None and high < fvalue:
            return high

        return fvalue

    def _make_text_entry(self, control, fvalue_text, size=wx.Size(56, 20)):
        if self.factory.enter_set:
            text = wx.TextCtrl(control,
                               -1,
                               fvalue_text,
                               size=size,
                               style=wx.TE_PROCESS_ENTER)
            control.Bind(wx.EVT_TEXT_ENTER, self.update_object_on_enter, id=text.GetId())
        else:
            text = wx.TextCtrl(control, -1, fvalue_text, size=size)

        text.Bind(wx.EVT_KILL_FOCUS, self.update_object_on_enter)
        if self.factory.auto_set:
            control.Bind(wx.EVT_TEXT, self.update_object_on_enter, id=text.GetId())
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
            self.control.text.SetBackgroundColour(color)
            self.control.text.Refresh()

    def update_object_on_enter(self, event):
        """Handles the user pressing the Enter key in the text field."""
        if isinstance(event, wx.FocusEvent):
            event.Skip()

        # It is possible the event is processed after the control is removed
        # from the editor
        if self.control is None:
            return

        try:
            value = ast.literal_eval(self.control.text.GetValue())
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
        self.control.text.SetValue(text)
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

    def _make_control(self, parent):

        low, high = self._get_current_range()
        fvalue = self._clip(self.value, low, high)
        fvalue_text = self.string_value(fvalue)

        size = self._get_default_size()

        control = TraitsUIPanel(parent, -1)
        control.label_lo = self._make_label_low(control, low, size)
        control.slider = self._make_slider(control, fvalue)
        control.label_hi = self._make_label_high(control, high, size)
        control.text = self._make_text_entry(control, fvalue_text)
        return control

    @staticmethod
    def _do_layout(control):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(control.label_lo, 0, wx.ALIGN_CENTER)
        sizer.Add(control.slider, 1, wx.EXPAND)
        sizer.Add(control.label_hi, 0, wx.ALIGN_CENTER)
        sizer.Add(control.text, 0, wx.LEFT | wx.EXPAND, 4)
        control.SetSizerAndFit(sizer)

    def _get_default_size(self):
        if self.factory.label_width > 0:
            return wx.Size(self.factory.label_width, 20)
        return wx.DefaultSize

    def _get_label_high(self, high):
        if self.factory.high_name != "":
            return self.string_value(high)
        return self.factory.high_label

    def _get_label_low(self, low):
        if self.factory.low_name != "":
            return self.string_value(low)
        return self.factory.low_label

    def _make_label_low(self, control, low, size):
        low_label = self._get_label_low(low)
        style = wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE
        label_lo = wx.StaticText(control, -1, low_label, size=size, style=style)
        self.set_tooltip(label_lo)

        return label_lo

    def _make_slider(self, control, fvalue):
        ivalue = self._convert_to_slider(fvalue)
        slider = Slider(control,
                        -1,
                        value=ivalue,
                        minValue=0,
                        maxValue=10000,
                        size=wx.Size(80, 20),
                        style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        slider.SetTickFreq(1000)
        slider.SetValue(1)
        slider.SetPageSize(1000)
        slider.SetLineSize(100)
        slider.Bind(wx.EVT_SCROLL, self.update_object_on_scroll)
        self.set_tooltip(slider)

        return slider

    def _make_label_high(self, control, high, size):
        high_label = self._get_label_high(high)
        label_hi = wx.StaticText(control, -1, high_label, size=size)
        self.set_tooltip(label_hi)
        return label_hi

    def update_object_on_scroll(self, event):
        """Handles the user changing the current slider value."""
        event_type = event.GetEventType()
        if (
            (event_type == wxEVT_SCROLL_ENDSCROLL)
            or (
                self.factory.auto_set
                and (event_type == wx.wxEVT_SCROLL_THUMBTRACK)
            )
            or (
                self.factory.enter_set
                and (event_type == wx.wxEVT_SCROLL_THUMBRELEASE)
            )
        ):
            value = self._convert_from_slider(event.GetPosition())
            try:
                self.ui_changing = True
                self.control.text.SetValue(self.string_value(value))
                self.value = value
            except TraitError:
                pass
            finally:
                self.ui_changing = False

    def _set_slider(self, value):
        """Updates the slider range controls."""
        low, high = self._get_current_range()
        self.control.label_lo.SetLabel(self.string_value(low))
        self.control.label_hi.SetLabel(self.string_value(high))
        ivalue = self._convert_to_slider(value)
        self.control.slider.SetValue(ivalue)

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
        control = super()._make_control(parent)
        low, high = self._get_current_range()

        control.button_lo = self._make_button_low(control, low)
        control.button_hi = self._make_button_high(control, high)
        return control

    @staticmethod
    def _do_layout(control):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(control.label_lo, 2, wx.ALIGN_CENTER)
        sizer.Add(control.button_lo, 1, wx.ALIGN_CENTER)
        sizer.Add(control.slider, 6, wx.EXPAND)
        sizer.Add(control.button_hi, 1, wx.ALIGN_CENTER)
        sizer.Add(control.label_hi, 2, wx.ALIGN_CENTER)
        sizer.Add(control.text, 0, wx.LEFT | wx.EXPAND, 4)
        control.SetSizerAndFit(sizer)

    def _make_button_low(self, control, low):
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, size=(15, 15))
        button_lo = wx.BitmapButton(control,
                                    -1,
                                    bitmap=bmp,
                                    size=(-1, 20),
                                    style=wx.BU_EXACTFIT | wx.NO_BORDER,
                                    name="button_lo")
        button_lo.Bind(wx.EVT_BUTTON, self.reduce_range)
        button_lo.Enable(self.low is None or low != self.low)
        return button_lo

    def _make_button_high(self, control, high):

        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, size=(15, 15))
        button_hi = wx.BitmapButton(control,
                                    -1,
                                    bitmap=bmp,
                                    size=(-1, 20),
                                    style=wx.BU_EXACTFIT | wx.NO_BORDER,
                                    name="button_hi")
        button_hi.Bind(wx.EVT_BUTTON, self.increase_range)
        button_hi.Enable(self.high is None or high != self.high)
        return button_hi

    def _set_slider(self, value):
        """Updates the slider range controls."""
        low, high = self._get_current_range()
        if not low <= value <= high:
            low, high = self.init_current_range(value)

        ivalue = self._convert_to_slider(value)
        self.control.slider.SetValue(ivalue)

        fmt = self._get_format()
        self.control.label_lo.SetLabel(fmt % low)
        self.control.label_hi.SetLabel(fmt % high)
        self.control.button_lo.Enable(self.low is None or low != self.low)
        self.control.button_hi.Enable(self.high is None or high != self.high)

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

    def reduce_range(self, event):
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

    def increase_range(self, event):
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

    def _make_control(self, parent):

        low, high = self._get_current_range()
        fvalue = self._clip(self.value, low, high)
        fvalue_text = self.string_value(fvalue)

        control = TraitsUIPanel(parent, -1)
        control.text = self._make_text_entry(control, fvalue_text)
        control.button_lo = self._make_button_low(control, fvalue)
        control.button_hi = self._make_button_high(control, fvalue)
        return control

    def _make_text_entry(self, control, fvalue_text, size=wx.Size(41, 20)):
        text = super()._make_text_entry(control, fvalue_text, size)
        text.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        text.Bind(wx.EVT_CHAR, self.on_char)
        return text

    @staticmethod
    def _do_layout(control):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(control.text, 12, wx.LEFT | wx.EXPAND)
        spinctrl_sizer = wx.BoxSizer(wx.VERTICAL)
        spinctrl_sizer.Add(control.button_hi, 1, wx.ALIGN_CENTER)
        spinctrl_sizer.Add(control.button_lo, 1, wx.ALIGN_CENTER)
        sizer.Add(spinctrl_sizer, 1, wx.RIGHT)
        control.SetSizerAndFit(sizer)

    def _make_button_low(self, control, value):
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, size=(15, 10))
        button_lo = wx.BitmapButton(control,
                                    -1,
                                    bitmap=bmp,
                                    size=(15, 12),
                                    style=wx.BU_EXACTFIT | wx.NO_BORDER,
                                    name="button_lo")
        # button_lo.Bind(wx.EVT_BUTTON, self.spin_down)
        button_lo.Bind(wx.EVT_LEFT_DOWN, self.spin_down)
        button_lo.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        button_lo.Enable(self.low is None or self.low < value)
        return button_lo

    def _make_button_high(self, control, value):

        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_UP, size=(15, 10))
        button_hi = wx.BitmapButton(control,
                                    -1,
                                    bitmap=bmp,
                                    size=(15, 12),
                                    style=wx.BU_EXACTFIT | wx.NO_BORDER,
                                    name="button_hi")
        # button_hi.Bind(wx.EVT_BUTTON, self.spin_up)
        button_hi.Bind(wx.EVT_LEFT_DOWN, self.spin_up)
        button_hi.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

        button_hi.Enable(self.high is None or value < self.high)
        return button_hi

    def _spin(self, step):

        low, high = self._get_current_range()
        value = self._clip(Decimal(str(self.value)) + step, low, high)

        if self.factory.is_float is False:
            value = int(value)
        self.value = value
        self.update_editor()

    def _get_modifier(self, event):

        modifier = Decimal(str(self.step))
        if event.ShiftDown():
            modifier *= 2
        if event.ControlDown():
            modifier *= 10
        if event.AltDown():
            modifier *= 100
        return modifier

    def on_char(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP:
            self.spin_up(event)
        elif keycode == wx.WXK_DOWN:
            self.spin_down(event)
        elif keycode == wx.WXK_PAGEUP:
            self.spin_up(event, 10)
        elif keycode == wx.WXK_PAGEDOWN:
            self.spin_down(event, 10)
        else:
            event.Skip()

    def spin_down(self, event, fact=1):
        """Reduces the value."""
        step = -1 * self._get_modifier(event) * fact
        self._spin(step)

    def spin_up(self, event, fact=1):
        """Increases the value."""
        step = self._get_modifier(event) * fact
        self._spin(step)

    def on_mouse_wheel(self, event):
        sign = -1 if event.WheelRotation < 0 else 1
        step = sign * self._get_modifier(event)
        self._spin(step)

    def _set_slider(self, value):
        """Updates the spinbutton controls."""
        low, high = self._get_current_range()
        self.control.button_lo.Enable(low is None or low < value)
        self.control.button_hi.Enable(high is None or value < high)


class RangeTextEditor(BaseRangeEditor):
    """Editor for ranges that displays a text field.

    If the user enters a value that is outside the allowed range,
    the background of the field changes color to indicate an error.
    """

    def _make_control(self, parent):

        low, high = self._get_current_range()
        fvalue = self._clip(self.value, low, high)
        fvalue_text = self.string_value(fvalue)

        control = TraitsUIPanel(parent, -1)
        control.text = self._make_text_entry(control, fvalue_text)
        return control

    @staticmethod
    def _do_layout(control):
        pass


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
