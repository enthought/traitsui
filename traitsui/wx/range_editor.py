#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the various range editors for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import sys
import wx

from math \
    import log10

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
    import TraitsUIPanel, Slider


if not hasattr(wx, 'wx.wxEVT_SCROLL_ENDSCROLL'):
    wxEVT_SCROLL_ENDSCROLL = wx.wxEVT_SCROLL_CHANGED
else:
    wxEVT_SCROLL_ENDSCROLL = wx.wxEVT_SCROLL_ENDSCROLL


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
        if not factory.low_name:
            self.low = factory.low

        if not factory.high_name:
            self.high = factory.high

        self.format = factory.format

        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        size = wx.DefaultSize
        if factory.label_width > 0:
            size = wx.Size(factory.label_width, 20)

        self.sync_value(factory.low_name, 'low', 'from')
        self.sync_value(factory.high_name, 'high', 'from')
        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        fvalue = self.value

        if not (self.low <= fvalue <= self.high):
            fvalue_text = ''
            fvalue = self.low
        else:
            try:
                fvalue_text = self.format % fvalue
            except (ValueError, TypeError) as e:
                fvalue_text = ''

        ivalue = self._convert_to_slider(fvalue)

        self._label_lo = wx.StaticText(
            panel, -1, '999999', size=size, style=wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)
        sizer.Add(self._label_lo, 0, wx.ALIGN_CENTER)
        panel.slider = slider = Slider(panel, -1, ivalue, 0, 10000,
                                       size=wx.Size(80, 20),
                                       style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        slider.SetTickFreq(1000)
        slider.SetValue(1)
        slider.SetPageSize(1000)
        slider.SetLineSize(100)
        wx.EVT_SCROLL(slider, self.update_object_on_scroll)
        sizer.Add(slider, 1, wx.EXPAND)
        self._label_hi = wx.StaticText(panel, -1, '999999', size=size)
        sizer.Add(self._label_hi, 0, wx.ALIGN_CENTER)

        panel.text = text = wx.TextCtrl(panel, -1, fvalue_text,
                                        size=wx.Size(56, 20),
                                        style=wx.TE_PROCESS_ENTER)
        wx.EVT_TEXT_ENTER(panel, text.GetId(), self.update_object_on_enter)
        wx.EVT_KILL_FOCUS(text, self.update_object_on_enter)

        sizer.Add(text, 0, wx.LEFT | wx.EXPAND, 4)

        low_label = factory.low_label
        if factory.low_name != '':
            low_label = self.format % self.low

        high_label = factory.high_label
        if factory.high_name != '':
            high_label = self.format % self.high

        self._label_lo.SetLabel(low_label)
        self._label_hi.SetLabel(high_label)
        self.set_tooltip(slider)
        self.set_tooltip(self._label_lo)
        self.set_tooltip(self._label_hi)
        self.set_tooltip(text)

        # Set-up the layout:
        panel.SetSizerAndFit(sizer)

    #-------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #-------------------------------------------------------------------------

    def update_object_on_scroll(self, event):
        """ Handles the user changing the current slider value.
        """
        value = self._convert_from_slider(event.GetPosition())
        event_type = event.GetEventType()
        if ((event_type == wxEVT_SCROLL_ENDSCROLL) or
            (self.factory.auto_set and
             (event_type == wx.wxEVT_SCROLL_THUMBTRACK)) or
            (self.factory.enter_set and
             (event_type == wx.wxEVT_SCROLL_THUMBRELEASE))):
            try:
                self.ui_changing = True
                self.control.text.SetValue(self.format % value)
                self.value = value
            except TraitError:
                pass
            finally:
                self.ui_changing = False

    #-------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #-------------------------------------------------------------------------

    def update_object_on_enter(self, event):
        """ Handles the user pressing the Enter key in the text field.
        """
        if isinstance(event, wx.FocusEvent):
            event.Skip()

        # There are cases where this method is called with self.control ==
        # None.
        if self.control is None:
            return

        try:
            try:
                value = self.control.text.GetValue().strip()
                if self.factory.is_float:
                    value = float(value)
                else:
                    value = int(value)
            except Exception as ex:
                # The user entered something that didn't eval as a number (e.g., 'foo').
                # Pretend it didn't happen (i.e. do not change self.value).
                value = self.value
                self.control.text.SetValue(str(value))
                # for compound editor, value may be non-numeric
                if not isinstance(value, (int, float)):
                    return

            self.value = value
            if not self.ui_changing:
                self.control.slider.SetValue(
                    self._convert_to_slider(self.value))
            self.control.text.SetBackgroundColour(OKColor)
            self.control.text.Refresh()
            if self._error is not None:
                self._error = None
                self.ui.errors -= 1
        except TraitError:
            pass

    #-------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #-------------------------------------------------------------------------

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        if self._error is None:
            self._error = True
            self.ui.errors += 1
            super(SimpleSliderEditor, self).error(excp)
        self.set_error_state(True)

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        try:
            text = self.format % value
            1 / (self.low <= value <= self.high)
        except:
            text = ''
            value = self.low

        ivalue = self._convert_to_slider(value)
        self.control.text.SetValue(text)
        self.control.slider.SetValue(ivalue)

    def _convert_to_slider(self, value):
        """ Returns the slider setting corresponding to the user-supplied value.
        """
        if self.high > self.low:
            ivalue = int((float(value - self.low) /
                          (self.high - self.low)) * 10000.0)
        else:
            ivalue = self.low
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
            self._label_lo.SetLabel(self.format % low)
            self.update_editor()

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)

        if self._label_hi is not None:
            self._label_hi.SetLabel(self.format % high)
            self.update_editor()


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

       The editor displays a slider and a text field. A subset of the total
       range is displayed in the slider; arrow buttons at each end of the
       slider let the user move the displayed range higher or lower.
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
        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
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
        label_lo = wx.StaticText(panel, -1, '999999')
        panel.label_lo = label_lo
        sizer.Add(label_lo, 2, wx.ALIGN_CENTER)

        # Lower limit button:
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK,
                                       size=(15, 15))
        button_lo = wx.BitmapButton(panel, -1, bitmap=bmp, size=(-1, 20),
                                    style=wx.BU_EXACTFIT | wx.NO_BORDER)
        panel.button_lo = button_lo
        button_lo.Bind(wx.EVT_BUTTON, self.reduce_range, button_lo)
        sizer.Add(button_lo, 1, wx.ALIGN_CENTER)

        # Slider:
        panel.slider = slider = Slider(panel, -1, ivalue, 0, 10000,
                                       size=wx.Size(80, 20),
                                       style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        slider.SetTickFreq(1000)
        slider.SetValue(1)
        slider.SetPageSize(1000)
        slider.SetLineSize(100)
        wx.EVT_SCROLL(slider, self.update_object_on_scroll)
        sizer.Add(slider, 6, wx.EXPAND)

        # Upper limit button:
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                       size=(15, 15))
        button_hi = wx.BitmapButton(panel, -1, bitmap=bmp, size=(-1, 20),
                                    style=wx.BU_EXACTFIT | wx.NO_BORDER)
        panel.button_hi = button_hi
        button_hi.Bind(wx.EVT_BUTTON, self.increase_range, button_hi)
        sizer.Add(button_hi, 1, wx.ALIGN_CENTER)

        # Upper limit label:
        label_hi = wx.StaticText(panel, -1, '999999')
        panel.label_hi = label_hi
        sizer.Add(label_hi, 2, wx.ALIGN_CENTER)

        # Text entry:
        panel.text = text = wx.TextCtrl(panel, -1, fvalue_text,
                                        size=wx.Size(56, 20),
                                        style=wx.TE_PROCESS_ENTER)
        wx.EVT_TEXT_ENTER(panel, text.GetId(), self.update_object_on_enter)
        wx.EVT_KILL_FOCUS(text, self.update_object_on_enter)

        sizer.Add(text, 0, wx.LEFT | wx.EXPAND, 4)

        # Set-up the layout:
        panel.SetSizerAndFit(sizer)
        label_lo.SetLabel(str(low))
        label_hi.SetLabel(str(high))
        self.set_tooltip(slider)
        self.set_tooltip(label_lo)
        self.set_tooltip(label_hi)
        self.set_tooltip(text)

        # Update the ranges and button just in case.
        self.update_range_ui()

    #-------------------------------------------------------------------------
    #  Handles the user changing the current slider value:
    #-------------------------------------------------------------------------

    def update_object_on_scroll(self, event):
        """ Handles the user changing the current slider value.
        """
        low = self.cur_low
        high = self.cur_high
        value = low + ((float(event.GetPosition()) / 10000.0) *
                       (high - low))
        self.control.text.SetValue(self._format % value)
        event_type = event.GetEventType()
        try:
            self.ui_changing = True
            if ((event_type == wxEVT_SCROLL_ENDSCROLL) or
                (self.factory.auto_set and
                 (event_type == wx.wxEVT_SCROLL_THUMBTRACK)) or
                (self.factory.enter_set and
                 (event_type == wx.wxEVT_SCROLL_THUMBRELEASE))):
                if self.factory.is_float:
                    self.value = value
                else:
                    self.value = int(value)
        finally:
            self.ui_changing = False

    #-------------------------------------------------------------------------
    #  Handle the user pressing the 'Enter' key in the edit control:
    #-------------------------------------------------------------------------

    def update_object_on_enter(self, event):
        """ Handles the user pressing the Enter key in the text field.
        """
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        try:
            value = self.control.text.GetValue().strip()
            try:
                if self.factory.is_float:
                    value = float(value)
                else:
                    value = int(value)
            except Exception as ex:
                # The user entered something that didn't eval as a number (e.g., 'foo').
                # Pretend it didn't happen (i.e. do not change self.value).
                value = self.value
                self.control.text.SetValue(str(value))

            self.value = value
            self.control.text.SetBackgroundColour(OKColor)
            self.control.text.Refresh()
            # Update the slider range.
            # Set ui_changing to True to avoid recursion:
            # the update_range_ui method will try to set the value in the text
            # box, which will again fire this method if auto_set is True.
            if not self.ui_changing:
                self.ui_changing = True
                self.init_range()
                self.update_range_ui()
                self.ui_changing = False
            if self._error is not None:
                self._error = None
                self.ui.errors -= 1
        except TraitError as excp:
            pass

    #-------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #-------------------------------------------------------------------------

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        if self._error is None:
            self._error = True
            self.ui.errors += 1
            super(LargeRangeSliderEditor, self).error(excp)
        self.set_error_state(True)

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
        self.control.label_lo.SetLabel(self._format % low)
        self.control.label_hi.SetLabel(self._format % high)
        if high > low:
            ivalue = int((float(value - low) / (high - low)) * 10000.0)
        else:
            ivalue = low
        self.control.slider.SetValue(ivalue)
        text = self._format % self.value
        self.control.text.SetValue(text)
        factory = self.factory
        f_low, f_high = self.low, self.high

        if low == f_low:
            self.control.button_lo.Disable()
        else:
            self.control.button_lo.Enable()

        if high == f_high:
            self.control.button_hi.Disable()
        else:
            self.control.button_hi.Enable()

    def init_range(self):
        """ Initializes the slider range controls.
        """
        value = self.value
        factory = self.factory
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

    def reduce_range(self, event):
        """ Reduces the extent of the displayed range.
        """
        factory = self.factory
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

    def increase_range(self, event):
        """ Increased the extent of the displayed range.
        """
        factory = self.factory
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
        self.control = wx.SpinCtrl(parent, -1, self.str_value,
                                   min=low,
                                   max=high,
                                   initial=self.value)
        wx.EVT_SPINCTRL(parent, self.control.GetId(), self.update_object)
        if wx.VERSION < (3, 0):
            wx.EVT_TEXT(parent, self.control.GetId(), self.update_object)
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Handle the user selecting a new value from the spin control:
    #-------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user selecting a new value in the spin box.
        """
        if self.control is None:
            return
        self._locked = True
        try:
            self.value = self.control.GetValue()
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
            try:
                self.control.SetValue(int(self.value))
            except:
                pass

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
            self.control.SetRange(self.low, self.high)
            self.control.SetValue(int(self.value))

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)
        if self.control:
            self.control.SetRange(self.low, self.high)
            self.control.SetValue(int(self.value))

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

    # Low value for the slider range
    low = Any

    # High value for the slider range
    high = Any

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
        if not self.factory.low_name:
            self.low = self.factory.low

        if not self.factory.high_name:
            self.high = self.factory.high

        self.sync_value(self.factory.low_name, 'low', 'from')
        self.sync_value(self.factory.high_name, 'high', 'from')

        if self.factory.enter_set:
            control = wx.TextCtrl(parent, -1, self.str_value,
                                  style=wx.TE_PROCESS_ENTER)
            wx.EVT_TEXT_ENTER(parent, control.GetId(), self.update_object)
        else:
            control = wx.TextCtrl(parent, -1, self.str_value)

        wx.EVT_KILL_FOCUS(control, self.update_object)

        if self.factory.auto_set:
            wx.EVT_TEXT(parent, control.GetId(), self.update_object)

        self.evaluate = self.factory.evaluate
        self.sync_value(self.factory.evaluate_name, 'evaluate', 'from')

        self.control = control
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """
        if isinstance(event, wx.FocusEvent):
            event.Skip()

        # There are cases where this method is called with self.control ==
        # None.
        if self.control is None:
            return

        value = self.control.GetValue()

        # Try to convert the string value entered by the user to a numerical
        # value.
        try:
            if self.evaluate is not None:
                value = self.evaluate(value)
            else:
                if self.factory.is_float:
                    value = float(value)
                else:
                    value = int(value)
        except Exception as excp:
            # The conversion failed.
            self.error(excp)
            return

        if value < self.low or value > self.high:
            self.set_error_state(True)
            return

        # Try to assign the numerical value to the trait.
        # This may fail because of constraints on the trait.
        try:
            self.value = value
            self.control.SetBackgroundColour(OKColor)
            self.control.Refresh()
            if self._error is not None:
                self._error = None
                self.ui.errors -= 1
        except TraitError as excp:
            pass

    #-------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #-------------------------------------------------------------------------

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        if self._error is None:
            self._error = True
            self.ui.errors += 1
            super(RangeTextEditor, self).error(excp)
        self.set_error_state(True)

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
            self.control.SetValue(int(self.value))

    def _high_changed(self, high):
        if self.value > high:
            if self.factory.is_float:
                self.value = float(high)
            else:
                self.value = int(high)
        if self.control:
            self.control.SetValue(int(self.value))

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

### EOF #######################################################################
